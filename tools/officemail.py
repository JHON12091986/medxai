import json, logging, time
from exchangelib import Credentials, Account, DELEGATE, Configuration, Build, Version

logger     = logging.getLogger("nina.tools.email")
access_log = logging.getLogger("nina.email_access")

def _log_access(mailbox: str, count: int):
    access_log.info(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S.000+0600"),
                                 "mailbox": mailbox, "emails_fetched": count}))

async def fetch(config) -> str:
    results = []
    for email_addr, label in [(config.ews_my_email, "Personal"), (config.ews_shared_email, "BasicID")]:
        try:
            creds = Credentials(f"{config.ews_domain}\\{config.ews_username}", config.ews_password)
            cfg   = Configuration(server=config.ews_server, credentials=creds,
                                  auth_type="NTLM",
                                  version=Version(Build(15, 1)))
            acct  = Account(email_addr, config=cfg, autodiscover=False, access_type=DELEGATE)
            items = list(acct.inbox.filter(is_read=False).order_by("-datetime_received")[:config.ews_max_emails])
            _log_access(email_addr, len(items))
            kw = [k.lower() for k in config.ews_keywords.split(",")]
            urgent = [i for i in items if any(k in (i.subject or "").lower() for k in kw)]
            results.append(f"**{label}** — {len(items)} unread, {len(urgent)} urgent")
            for i in urgent[:3]:
                results.append(f"  • {i.subject} | {i.sender.email_address if i.sender else 'unknown'}")
        except Exception as e:
            logger.error(f"morning_report_ews_fetch_failed mailbox={email_addr} err={e}",
                         extra={"log":"error.log", "tool_name": "officemail"})
            results.append(f"**{label}** — Unavailable (EWS unreachable, retry at next report)")
    return "\n".join(results)
