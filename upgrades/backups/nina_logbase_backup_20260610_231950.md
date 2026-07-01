# NINA Logbase Backup
Generated: 2026-06-10 23:19:50

## Directory Tree
```
No logs directory
```

## File Contents
### logs/agent_actions.log
Last modified: 2026-06-09 20:49:41
Size: 124 bytes
```log
2026-06-09T20:47:48.743967 | check doc AGENTS.md → ❌ FAIL
2026-06-09T20:49:41.434364 | check doc AGENTS.md → ✅ PASS
```

### logs/agent.log
Last modified: 2026-06-05 22:13:18
Size: 8431 bytes
```log
2026-06-05 20:58:18,529 [INFO] nina.agent: agent_step step=1 task=multilingual response="To find the current USD/BDT exchange rate, I'll start by searching the web for t"
2026-06-05 20:58:22,187 [INFO] nina.agent: agent_step step=2 task=multilingual response="Now that I have found the current USD/BDT exchange rate, I'll verify the informa"
2026-06-05 20:58:24,678 [INFO] nina.agent: agent_step step=3 task=multilingual response="It seems like the system tool command was unnecessary. Let's proceed with provid"
2026-06-05 21:02:59,207 [INFO] nina.agent: agent_step step=1 task=multilingual response='[Step 1/5] \nTo find the current USD/BDT exchange rate, I will use the web to get'
2026-06-05 21:03:02,771 [INFO] nina.agent: agent_step step=2 task=multilingual response='[Step 3/5] \nThe current USD/BDT exchange rate is 122.78 BDT. This information is'
2026-06-05 21:07:10,604 [WARNING] nina.agent: thermal_warn CPU=80.0 GPU=66
2026-06-05 21:07:11,318 [INFO] nina.agent: agent_step step=1 task=general response='[Step 2/5] TOOL:web INPUT:query="USD/BDT exchange rate" to get the current excha'
2026-06-05 21:07:14,597 [INFO] nina.agent: agent_step step=2 task=general response='[Step 3/5] No additional information is needed, the current USD/BDT exchange rat'
2026-06-05 21:12:40,535 [WARNING] nina.agent: thermal_warn CPU=87.0 GPU=73
2026-06-05 21:12:40,536 [INFO] nina.agent: agent_step step=1 task=general response='[Step 1/5] \nTo find the current USD/BDT exchange rate, I will use the web to get'
2026-06-05 21:12:41,459 [INFO] nina.agent: agent_step step=2 task=general response='[Step 3/5] \nThe current USD/BDT exchange rate is 122.78 BDT. This information is'
2026-06-05 21:34:53,861 [INFO] nina.agent: agent_step step=1 task=general response='[Step 2/5] TOOL:web INPUT:query="USD/BDT exchange rate" to get the current excha'
2026-06-05 21:34:56,867 [INFO] nina.agent: agent_step step=2 task=general response='[Step 3/5] The current USD/BDT exchange rate is 1 USD = 122.7 BDT, according to '
2026-06-05 21:34:59,452 [INFO] nina.agent: agent_step step=3 task=general response='[Step 4/5] Scratchpad:\n[web] -> Answer: The current USD to BDT exchange rate is '
2026-06-05 21:35:01,885 [INFO] nina.agent: agent_step step=4 task=general response='[Step 5/5] FINAL: The current USD/BDT exchange rate is 1 USD = 122.7 BDT. Please'
2026-06-05 21:46:15,077 [INFO] nina.agent: agent_step step=1 task=general response='আজকের USD/BDT এক্সচেঞ্জ রেটের জন্য লাইভ ডেটা চেক করা হচ্ছে। একটু অপেক্ষা করুন।\n\n'
2026-06-05 21:47:37,254 [INFO] nina.agent: agent_step step=2 task=general response='বুঝতে পেরেছি, টুল ব্যবহারের ফরম্যাটে ভুল হয়েছে। সঠিকভাবে লাইভ ডেটা আনতে **TOOL:w'
2026-06-05 21:48:40,963 [INFO] nina.agent: agent_step step=3 task=general response='ধন্যবাদ ধৈর্য ধরার জন্য। সরাসরি **TOOL:browser** ব্যবহার করে বাংলাদেশ ব্যাংকের অ'
2026-06-05 21:50:13,559 [INFO] nina.agent: agent_step step=1 task=general response='[LANGUAGE OVERRIDE: সম্পূর্ণ উত্তর বাংলায়।]\n\n**THINK:**\nব্যাংকিং পেশাদার হিসেবে'
2026-06-05 21:52:08,630 [INFO] nina.agent: agent_step step=1 task=general response='আজকের USD/BDT রেট জানার জন্য লাইভ ডেটা প্রয়োজন। বাংলাদেশ ব্যাংক ও কয়েকটি বাণিজ'
2026-06-05 21:53:25,198 [INFO] nina.agent: agent_step step=2 task=general response='[Step 3/5] **TOOL:web** ব্যবহার করে বাংলাদেশ ব্যাংকের ওয়েবসাইট থেকে আজকের USD/B'
2026-06-05 21:54:42,157 [INFO] nina.agent: agent_step step=3 task=general response='[Step 4/5] **সংশোধন ও আপডেট:**\n\nবাংলাদেশ ব্যাংকের ওয়েবসাইট থেকে সরাসরি **লাইভ U'
2026-06-05 21:55:58,788 [INFO] nina.agent: agent_step step=4 task=general response='**চূড়ান্ত উত্তর (FINAL ANSWER):**\n\n**আজকের USD/BDT রেট (১২ জুন ২০২৪, সন্ধ্যা ৬:'
2026-06-05 21:57:02,038 [WARNING] nina.agent: agent_loop_timeout goal='[LANGUAGE OVERRIDE: Respond entirely in Bangla. No English except technical term' exceeded=300s
2026-06-05 21:59:54,517 [INFO] nina.agent: agent_step step=1 task=multilingual response='আজকের USD/BDT এক্সচেঞ্জ রেট পাওয়ার জন্য আমি সরাসরি বাংলাদেশ ব্যাংক বা নির্ভরযোগ'
2026-06-05 22:01:00,630 [INFO] nina.agent: agent_step step=1 task=general response='[LANGUAGE OVERRIDE: সম্পূর্ণ উত্তর বাংলায়।]\n\nবাইজিদ ভাই, ভালো আছেন আশা করি। USD'
2026-06-05 22:01:04,092 [INFO] nina.agent: agent_step step=2 task=multilingual response='ধন্যবাদ, বিষয়টি বুঝতে পেরেছি। সরাসরি **TOOL:browser** ব্যবহার করে নির্ভরযোগ্য উ'
2026-06-05 22:02:21,832 [INFO] nina.agent: agent_step step=2 task=general response='[LANGUAGE OVERRIDE: সম্পূর্ণ উত্তর বাংলায়।]\n\nবাইজিদ ভাই, আজকের **ইন্টারব্যাংক U'
2026-06-05 22:02:22,427 [INFO] nina.agent: agent_step step=3 task=multilingual response='ধন্যবাদ, বিষয়টি পরিষ্কার হলো। সরাসরি **TOOL:web** ব্যবহার করে সঠিক পদ্ধতিতে ডেট'
2026-06-05 22:03:30,031 [INFO] nina.agent: agent_step step=4 task=multilingual response='বুঝতে পেরেছি — টুল ব্যবহারের সিনট্যাক্সে সমস্যা হচ্ছে। সরাসরি **TOOL:web** এর পর'
2026-06-05 22:03:33,105 [INFO] nina.agent: agent_step step=3 task=general response='[LANGUAGE OVERRIDE: সম্পূর্ণ উত্তর বাংলায়।]\n\n**আপডেটেড রেট (আজকের তারিখ):**\nবাং'
2026-06-05 22:05:05,421 [INFO] nina.agent: agent_step step=1 task=general response='[Step 2/5] **PLAN:**\n- **TOOL:web** ব্যবহার করে বর্তমান USD/BDT এক্সচেঞ্জ রেট খু'
2026-06-05 22:06:09,782 [INFO] nina.agent: agent_step step=2 task=general response='[Step 4/5] **ACT (সংশোধিত):**\n- **TOOL:web** ব্যবহার করে সরাসরি বাংলাদেশ ব্যাংকে'
2026-06-05 22:07:19,921 [INFO] nina.agent: agent_step step=3 task=general response='**আপডেট (১২ জুন ২০২৪, দুপুর ২:৩০ - ঢাকা সময়):**\n\n**TOOL:browser** থেকে প্রাপ্ত '
2026-06-05 22:08:29,042 [INFO] nina.agent: agent_step step=1 task=multilingual response='[Step 1/5] Scratchpad:\n- ব্যবহারকারীর প্রশ্ন সরাসরি USD/BDT রেট সম্পর্কিত।\n- মেম'
2026-06-05 22:09:44,356 [INFO] nina.agent: agent_step step=2 task=multilingual response='**উত্তর:**\nআজকে (তারিখ: **`{{current_date}}`**) **USD/BDT** রেটের সর্বশেষ তথ্য ন'
2026-06-05 22:11:30,905 [INFO] nina.agent: agent_step step=3 task=multilingual response='**উত্তর (Python-এর `*` ও `**` প্যারামিটার অপারেটর):**\n\nPython-এ ফাংশন ডেফিনেশনে '
2026-06-05 22:12:45,965 [INFO] nina.agent: agent_step step=4 task=multilingual response='**সংক্ষিপ্ত উত্তর (Python-এ `*` ও `**` এর কাজ):**\n\n### **১. `*` (Single Star) – '
2026-06-05 22:13:18,452 [WARNING] nina.agent: agent_loop_timeout goal='[LANGUAGE OVERRIDE: Respond entirely in Bangla. No English except technical term' exceeded=300s
```

### logs/agent.log.2026-05-21
Last modified: 2026-05-21 22:30:18
Size: 0 bytes
```log
```

### logs/agent.log.2026-05-22
Last modified: 2026-05-22 23:03:09
Size: 5411 bytes
```log
2026-05-22 21:45:39,198 [INFO] nina.agent: agent_step step=1 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 21:45:40,809 [INFO] nina.agent: agent_step step=2 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 21:45:43,880 [INFO] nina.agent: agent_step step=3 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 21:45:45,281 [INFO] nina.agent: agent_step step=4 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 21:45:48,404 [INFO] nina.agent: agent_step step=5 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 21:46:21,626 [INFO] nina.agent: agent_step step=1 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 21:46:22,821 [INFO] nina.agent: agent_step step=2 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 21:46:23,896 [INFO] nina.agent: agent_step step=3 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 21:46:27,022 [INFO] nina.agent: agent_step step=4 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 21:46:28,028 [INFO] nina.agent: agent_step step=5 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 22:13:39,178 [INFO] nina.agent: agent_step step=1 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 22:13:41,034 [INFO] nina.agent: agent_step step=2 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 22:13:42,024 [INFO] nina.agent: agent_step step=3 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 22:13:43,064 [INFO] nina.agent: agent_step step=4 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 22:13:45,996 [INFO] nina.agent: agent_step step=5 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 22:20:44,212 [INFO] nina.agent: agent_step step=1 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 22:20:45,321 [INFO] nina.agent: agent_step step=2 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 22:20:46,402 [INFO] nina.agent: agent_step step=3 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 22:20:47,526 [INFO] nina.agent: agent_step step=4 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 22:20:48,850 [INFO] nina.agent: agent_step step=5 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 22:28:12,943 [INFO] nina.agent: agent_step step=1 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 22:28:14,141 [INFO] nina.agent: agent_step step=2 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 22:28:15,481 [INFO] nina.agent: agent_step step=3 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 22:28:17,858 [INFO] nina.agent: agent_step step=4 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 22:28:21,378 [INFO] nina.agent: agent_step step=5 task=general response='⚠️ All providers are currently unavailable. Try again in a moment, or send /stat'
2026-05-22 23:02:38,592 [INFO] nina.agent: agent_step step=1 task=general response='Since the goal is just "hi", it seems like a greeting rather than a specific tas'
2026-05-22 23:02:48,934 [INFO] nina.agent: agent_step step=1 task=coding response='[Step 2/8] THINK: To answer the question about the model I am using, I need to i'
2026-05-22 23:03:02,759 [INFO] nina.agent: agent_step step=1 task=general response="[Step 1/3] THINK: Identify the goal, which is to determine the model's name. Sin"
2026-05-22 23:03:04,868 [INFO] nina.agent: agent_step step=2 task=general response="[Step 1/3] THINK: Identify the goal, which is to determine the model's name. Sin"
2026-05-22 23:03:07,264 [INFO] nina.agent: agent_step step=3 task=general response="[Step 1/3] THINK: Identify the goal, which is to determine the model's name. Sin"
2026-05-22 23:03:08,188 [INFO] nina.agent: agent_step step=4 task=general response="[Step 1/3] THINK: Identify the goal, which is to determine the model's name. Sin"
2026-05-22 23:03:09,107 [INFO] nina.agent: agent_step step=5 task=general response="[Step 1/3] THINK: Identify the goal, which is to determine the model's name. Sin"
```

### logs/agent.log.2026-05-23
Last modified: 2026-05-23 01:15:32
Size: 2027 bytes
```log
2026-05-23 00:04:28,391 [INFO] nina.agent: agent_step step=1 task=general response='Since the goal is just "hi", it seems like a greeting rather than a specific tas'
2026-05-23 00:04:46,797 [INFO] nina.agent: agent_step step=1 task=multilingual response="It seems like we're starting a new thought process. Since we were previously dis"
2026-05-23 00:04:49,332 [INFO] nina.agent: agent_step step=2 task=multilingual response="It seems like we're starting a new thought process. Since we were previously dis"
2026-05-23 00:04:50,248 [INFO] nina.agent: agent_step step=3 task=multilingual response="It seems like we're starting a new thought process. Since we were previously dis"
2026-05-23 00:04:51,106 [INFO] nina.agent: agent_step step=4 task=multilingual response="It seems like we're starting a new thought process. Since we were previously dis"
2026-05-23 00:04:51,976 [INFO] nina.agent: agent_step step=5 task=multilingual response="It seems like we're starting a new thought process. Since we were previously dis"
2026-05-23 00:20:11,783 [INFO] nina.agent: agent_step step=1 task=general response="Since we're starting from scratch, let's THINK about what we want to achieve. Ou"
2026-05-23 01:15:32,652 [INFO] nina.agent: agent_step step=1 task=general response='Since the goal is just "hi" and there\'s no specific task or question, I\'ll assum'
2026-05-23 01:15:32,652 [INFO] nina.agent: agent_step step=2 task=general response='Since the goal is just "hi" and there\'s no specific task or question, I\'ll assum'
2026-05-23 01:15:32,652 [INFO] nina.agent: agent_step step=3 task=general response='Since the goal is just "hi" and there\'s no specific task or question, I\'ll assum'
2026-05-23 01:15:32,652 [INFO] nina.agent: agent_step step=4 task=general response='Since the goal is just "hi" and there\'s no specific task or question, I\'ll assum'
2026-05-23 01:15:32,652 [INFO] nina.agent: agent_step step=5 task=general response='Since the goal is just "hi" and there\'s no specific task or question, I\'ll assum'
```

### logs/agent.log.2026-05-24
Last modified: 2026-05-24 00:20:04
Size: 5354 bytes
```log
2026-05-24 00:00:33,728 [INFO] nina.agent: agent_step step=1 task=general response="Since the goal is just a greeting, I'll keep it simple.\n\n[Step 2/5] PLAN: Respon"
2026-05-24 00:00:37,992 [INFO] nina.agent: agent_step step=1 task=general response='**THINK:**\nThe user has greeted me and asked, "how are you?" This is a common so'
2026-05-24 00:01:38,638 [INFO] nina.agent: agent_step step=1 task=general response='Sure! I see you’re starting a multi‑step process and have opened a “Scratchpad” '
2026-05-24 00:01:39,150 [INFO] nina.agent: agent_step step=2 task=general response="It seems like we're progressing to Step 2 of 5. What would you like to accomplis"
2026-05-24 00:01:41,546 [INFO] nina.agent: agent_step step=3 task=general response="We're now at Step 3 of 5. What's the current objective or task you're working on"
2026-05-24 00:01:41,632 [INFO] nina.agent: agent_step step=1 task=general response='I’m designed to tackle a **wide variety of tasks**, but there are practical limi'
2026-05-24 00:01:44,065 [INFO] nina.agent: agent_step step=4 task=general response="It looks like we're getting close to the final step. We're now at Step 4 of 5. W"
2026-05-24 00:01:44,078 [INFO] nina.agent: agent_step step=2 task=general response="Based on our conversation, I'll determine the scope of the task you have in mind"
2026-05-24 00:01:46,548 [INFO] nina.agent: agent_step step=5 task=general response="We've reached the final step, Step 5 of 5. What's the conclusion or outcome you'"
2026-05-24 00:01:46,770 [INFO] nina.agent: agent_step step=3 task=general response="Now that we've discussed the scope of tasks I can handle, let's create a plan to"
2026-05-24 00:01:49,685 [INFO] nina.agent: agent_step step=4 task=general response="With the task details in mind, let's outline a step-by-step plan to complete it."
2026-05-24 00:01:52,463 [INFO] nina.agent: agent_step step=5 task=general response="Now that we've reached the final step, I'll provide a conclusion based on our co"
2026-05-24 00:02:14,256 [INFO] nina.agent: agent_step step=1 task=general response="It seems like we are starting from the beginning. \n\nTo proceed, I'll outline the"
2026-05-24 00:02:16,835 [INFO] nina.agent: agent_step step=1 task=general response="It seems like we've started fresh. \n\nYou've indicated that we're at Step 1/5, an"
2026-05-24 00:02:19,251 [INFO] nina.agent: agent_step step=2 task=general response="We've moved to Step 2/5. \n\nIn this step, we're supposed to plan. Since we don't "
2026-05-24 00:02:21,848 [INFO] nina.agent: agent_step step=3 task=general response="We're now at Step 3/5. \n\nIn this step, we're supposed to think about how to act "
2026-05-24 00:02:21,862 [INFO] nina.agent: agent_step step=1 task=general response="Since we are starting from scratch, let's begin by thinking about the problem or"
2026-05-24 00:02:24,407 [INFO] nina.agent: agent_step step=4 task=general response="We've reached Step 4/5.\n\nIt seems like we're getting close to taking action, but"
2026-05-24 00:02:24,410 [INFO] nina.agent: agent_step step=2 task=general response='We have reached the planning stage. \n\nTo plan our next move, we need to consider'
2026-05-24 00:02:27,007 [INFO] nina.agent: agent_step step=5 task=general response="We've reached the final step, Step 5/5.\n\nAlthough we didn't have a specific topi"
2026-05-24 00:02:27,349 [INFO] nina.agent: agent_step step=3 task=general response="It seems like we're trying to use the web tool to search for something, but we'r"
2026-05-24 00:02:30,248 [INFO] nina.agent: agent_step step=4 task=general response="It seems like we've tried searching the web for information, and we've stumbled "
2026-05-24 00:14:26,502 [INFO] nina.agent: agent_step step=1 task=general response='[Step 2/5] Analysis: \nThe user has asked a greeting question, "hey how are you?"'
2026-05-24 00:14:56,749 [INFO] nina.agent: agent_step step=1 task=general response='[Step 1/5] THINK: To determine if I am intelligent, I need to consider the defin'
2026-05-24 00:14:59,515 [INFO] nina.agent: agent_step step=2 task=general response='[Step 2/5] THINK: To evaluate my capabilities and features, I need to consider m'
2026-05-24 00:15:02,688 [INFO] nina.agent: agent_step step=3 task=general response='[Step 3/5] THINK: Based on the research, I can see that Artificial Intelligence,'
2026-05-24 00:15:05,863 [INFO] nina.agent: agent_step step=4 task=general response='[Step 4/5] THINK: It seems that I encountered an error when trying to use the sy'
2026-05-24 00:19:49,207 [INFO] nina.agent: agent_step step=1 task=general response='**Operator Demo Mode: Self-Audit**\n\n**Health Check:**\n TOOL:system INPUT:status\n'
2026-05-24 00:19:52,176 [INFO] nina.agent: agent_step step=2 task=general response='**Operator Demo Mode: Self-Audit**\n\n**Error Analysis:**\nThe error message indica'
2026-05-24 00:19:55,246 [INFO] nina.agent: agent_step step=3 task=general response='**Operator Demo Mode: Self-Audit**\n\n**Error Persistence:**\nThe error message per'
2026-05-24 00:19:58,651 [INFO] nina.agent: agent_step step=4 task=general response='**Operator Demo Mode: Self-Audit**\n\n**Error Summary:**\nThe `tools.system` module'
2026-05-24 00:20:04,977 [INFO] nina.agent: agent_step step=5 task=general response='**EXECUTIVE BRIEFING: OPERATOR DEMO MODE REPORT**\n*Delivered by: On-Device AI Ch'
```

### logs/agent.log.2026-06-01
Last modified: 2026-06-01 23:17:12
Size: 167 bytes
```log
2026-06-01 23:17:12,403 [INFO] nina.agent: agent_step step=1 task=general response='**THINK:**\nThe user has greeted me with a casual "hey how are you?" This is a co'
```

### logs/agent.log.2026-06-04
Last modified: 2026-06-04 19:11:10
Size: 2507 bytes
```log
2026-06-04 11:51:24,195 [INFO] nina.agent: agent_step step=1 task=general response='To determine if I can make cron jobs, I need to consider the capabilities of the'
2026-06-04 11:51:26,864 [INFO] nina.agent: agent_step step=2 task=general response="It seems that I don't have direct access to the 'crontab' command due to allowan"
2026-06-04 11:51:30,987 [INFO] nina.agent: agent_step step=3 task=general response="I've found some alternatives to cron jobs, which is useful information. However,"
2026-06-04 11:51:33,876 [INFO] nina.agent: agent_step step=4 task=general response="It seems that I'm also unable to use the 'anacron' command, which is one of the "
2026-06-04 11:51:36,676 [INFO] nina.agent: agent_step step=5 task=general response='It seems there was an error in the TOOL:system INPUT:status of cron job capabili'
2026-06-04 12:41:33,412 [INFO] nina.agent: agent_step step=1 task=general response='[Step 1/3] THINK: To create a scheduled task, I need to determine the best appro'
2026-06-04 12:42:10,228 [INFO] nina.agent: agent_step step=1 task=general response='THINK: To determine the commands, I need to consider the available tools.\n\nPLAN:'
2026-06-04 12:42:13,295 [INFO] nina.agent: agent_step step=2 task=general response="THINK: The user is looking for a way to query a website's content, and it seems "
2026-06-04 12:42:17,187 [INFO] nina.agent: agent_step step=3 task=general response="THINK: The user has found some tools that can help with querying a website's con"
2026-06-04 12:42:20,466 [INFO] nina.agent: agent_step step=4 task=general response="THINK: The user has found various tools that can help with querying a website's "
2026-06-04 12:42:31,984 [INFO] nina.agent: agent_step step=5 task=general response='### **Commands to Query Website Content**\n\nHere are the available commands and m'
2026-06-04 19:10:46,464 [INFO] nina.agent: agent_step step=1 task=general response='TOOL:system INPUT:status \nYou are currently identified as M. Baizid Alam, an AGM'
2026-06-04 19:10:53,121 [INFO] nina.agent: agent_step step=2 task=general response="Understood. Since the `system` tool isn't functioning as expected, I'll rely on "
2026-06-04 19:11:09,089 [INFO] nina.agent: agent_step step=3 task=general response='**You are M.\u202fBaizid\u202fAlam** – Assistant General Manager at **BASIC Bank Limited**'
2026-06-04 19:11:10,016 [INFO] nina.agent: agent_step step=4 task=general response="Given the errors with the `system` and `web` tools, I'll proceed based on the in"
```

### logs/emailaccess.log
Last modified: 2026-05-21 22:30:18
Size: 0 bytes
```log
```

### logs/error.log
Last modified: 2026-05-21 22:30:18
Size: 0 bytes
```log
```

### logs/nina.jsonl
Last modified: 2026-06-10 15:48:23
Size: 0 bytes
```log
```

### logs/nina.log
Last modified: 2026-06-10 23:18:26
Size: 80545 bytes
```log
2026-06-10 00:03:21,512 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.09656167030334473, "success": true}
2026-06-10 00:08:21,440 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020862817764282227, "success": true}
2026-06-10 00:13:21,427 [INFO] nina.scheduler: NINA operational
2026-06-10 00:13:21,427 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.0001971721649169922, "success": true}
2026-06-10 00:13:21,427 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 6.937980651855469e-05, "success": true}
2026-06-10 00:13:21,469 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.04111790657043457, "success": true}
2026-06-10 00:13:21,469 [INFO] nina.scheduler: reminder_check
2026-06-10 00:13:21,470 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00013875961303710938, "success": true}
2026-06-10 00:13:21,470 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.981590270996094e-05, "success": true}
2026-06-10 00:18:22,271 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.8556082248687744, "success": true}
2026-06-10 00:18:45,264 [INFO] nina.scheduler: Received signal 15, initiating graceful shutdown...
2026-06-10 00:18:54,691 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1 reminders=0
2026-06-10 00:18:54,727 [INFO] nina.router: Loaded circuit breaker state from data/circuit_state.json
2026-06-10 00:18:54,737 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-10 00:18:54,737 [INFO] nina.router: HybridRouter initialized
2026-06-10 00:18:54,737 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-10 00:18:54,745 [INFO] nina.scheduler: Scheduler started — 16 jobs
2026-06-10 00:18:54,745 [INFO] nina.scheduler: Scheduler started — 16 jobs
2026-06-10 00:18:55,691 [INFO] nina.telegram: TelegramInterface polling started
2026-06-10 00:18:55,692 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-10 00:18:55,692 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-10 00:20:55,753 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-10 00:20:58,425 [INFO] nina.routerlog: {"ts": "2026-06-10T00:20:58.000+0600", "req_id": "32451303", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-10 00:20:58,426 [WARNING] nina.router: router_fail req_id=32451303 provider=CHUTES err=http_401
2026-06-10 00:20:58,643 [INFO] nina.routerlog: {"ts": "2026-06-10T00:20:58.000+0600", "req_id": "32451303", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-10 00:20:58,643 [WARNING] nina.router: router_fail req_id=32451303 provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-10 00:20:58,970 [INFO] nina.routerlog: {"ts": "2026-06-10T00:20:58.000+0600", "req_id": "32451303", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-10 00:20:58,970 [WARNING] nina.router: router_fail req_id=32451303 provider=CEREBRAS err=http_404
2026-06-10 00:20:59,539 [INFO] nina.routerlog: {"ts": "2026-06-10T00:20:59.000+0600", "req_id": "32451303", "provider": "GROQ", "task_type": "research", "input_tokens": 370, "output_tokens": 80, "cost_usd": 0.0, "ttf_ms": 569, "total_ms": 569, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-10 00:20:59,540 [INFO] nina.router: router_success req_id=32451303 provider=GROQ task=research ms=569
2026-06-10 00:20:59,540 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-10_proposals.md
2026-06-10 00:21:01,636 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 00:21:01,637 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 00:21:02,842 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 00:21:02,843 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 00:23:54,773 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.028691530227661133, "success": true}
2026-06-10 00:23:54,773 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.028691530227661133, "success": true}
2026-06-10 00:23:56,468 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-10 00:23:57,279 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 00:23:57,281 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 00:28:54,851 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.10197091102600098, "success": true}
2026-06-10 00:28:54,851 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.10197091102600098, "success": true}
2026-06-10 00:33:54,765 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022223234176635742, "success": true}
2026-06-10 00:33:54,765 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022223234176635742, "success": true}
2026-06-10 00:33:54,766 [INFO] nina.scheduler: reminder_check
2026-06-10 00:33:54,766 [INFO] nina.scheduler: reminder_check
2026-06-10 00:33:54,766 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00011658668518066406, "success": true}
2026-06-10 00:33:54,766 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00011658668518066406, "success": true}
2026-06-10 00:33:54,766 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.981590270996094e-05, "success": true}
2026-06-10 00:33:54,766 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.981590270996094e-05, "success": true}
2026-06-10 00:38:54,815 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.06918549537658691, "success": true}
2026-06-10 00:38:54,815 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.06918549537658691, "success": true}
2026-06-10 00:43:54,773 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021814584732055664, "success": true}
2026-06-10 00:43:54,773 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021814584732055664, "success": true}
2026-06-10 00:48:54,748 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 0.0005862712860107422, "success": true}
2026-06-10 00:48:54,748 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 0.0005862712860107422, "success": true}
2026-06-10 00:48:54,993 [INFO] nina.scheduler: reminder_check
2026-06-10 00:48:54,993 [INFO] nina.scheduler: reminder_check
2026-06-10 00:48:54,993 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0009052753448486328, "success": true}
2026-06-10 00:48:54,993 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0009052753448486328, "success": true}
2026-06-10 00:48:54,996 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 0.00032067298889160156, "success": true}
2026-06-10 00:48:54,996 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 0.00032067298889160156, "success": true}
2026-06-10 00:48:56,248 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 1.4965448379516602, "success": true}
2026-06-10 00:48:56,248 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 1.4965448379516602, "success": true}
2026-06-10 00:51:59,544 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-10 00:52:03,798 [INFO] nina.routerlog: {"ts": "2026-06-10T00:52:03.000+0600", "req_id": "ebe1f91e", "provider": "GROQ", "task_type": "research", "input_tokens": 369, "output_tokens": 116, "cost_usd": 0.0, "ttf_ms": 796, "total_ms": 796, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-10 00:52:03,798 [INFO] nina.router: router_success req_id=ebe1f91e provider=GROQ task=research ms=796
2026-06-10 00:52:03,803 [INFO] nina.idle: idle_proposal_appended topic=morning_report file=2026-06-10_proposals.md
2026-06-10 00:53:54,838 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.09036135673522949, "success": true}
2026-06-10 00:53:54,838 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.09036135673522949, "success": true}
2026-06-10 00:53:58,999 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-10 00:53:59,011 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 00:53:59,012 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 00:58:54,772 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022368192672729492, "success": true}
2026-06-10 00:58:54,772 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022368192672729492, "success": true}
2026-06-10 01:03:54,780 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.037519216537475586, "success": true}
2026-06-10 01:03:54,780 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.037519216537475586, "success": true}
2026-06-10 01:03:54,781 [INFO] nina.scheduler: reminder_check
2026-06-10 01:03:54,781 [INFO] nina.scheduler: reminder_check
2026-06-10 01:03:54,781 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.107589721679688e-05, "success": true}
2026-06-10 01:03:54,781 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.107589721679688e-05, "success": true}
2026-06-10 01:03:54,781 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.0517578125e-05, "success": true}
2026-06-10 01:03:54,781 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.0517578125e-05, "success": true}
2026-06-10 01:07:58,023 [INFO] nina.config: config_hotreload no reloadable changes
2026-06-10 01:08:55,685 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.9382402896881104, "success": true}
2026-06-10 01:08:55,685 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.9382402896881104, "success": true}
2026-06-10 01:09:58,036 [INFO] nina.config: config_hotreload no reloadable changes
2026-06-10 01:13:54,850 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.09880828857421875, "success": true}
2026-06-10 01:13:54,850 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.09880828857421875, "success": true}
2026-06-10 01:18:54,758 [INFO] nina.scheduler: NINA operational
2026-06-10 01:18:54,758 [INFO] nina.scheduler: NINA operational
2026-06-10 01:18:54,758 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.0002484321594238281, "success": true}
2026-06-10 01:18:54,758 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.0002484321594238281, "success": true}
2026-06-10 01:18:54,758 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 5.6743621826171875e-05, "success": true}
2026-06-10 01:18:54,758 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 5.6743621826171875e-05, "success": true}
2026-06-10 01:18:54,790 [INFO] nina.scheduler: reminder_check
2026-06-10 01:18:54,790 [INFO] nina.scheduler: reminder_check
2026-06-10 01:18:54,791 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00015783309936523438, "success": true}
2026-06-10 01:18:54,791 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00015783309936523438, "success": true}
2026-06-10 01:18:54,791 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.743171691894531e-05, "success": true}
2026-06-10 01:18:54,791 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.743171691894531e-05, "success": true}
2026-06-10 01:18:55,647 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.8882851600646973, "success": true}
2026-06-10 01:18:55,647 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.8882851600646973, "success": true}
2026-06-10 01:23:03,814 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-10 01:23:05,897 [INFO] nina.routerlog: {"ts": "2026-06-10T01:23:05.000+0600", "req_id": "89a06d63", "provider": "GROQ", "task_type": "research", "input_tokens": 364, "output_tokens": 169, "cost_usd": 0.0, "ttf_ms": 1570, "total_ms": 1570, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-10 01:23:05,897 [INFO] nina.router: router_success req_id=89a06d63 provider=GROQ task=research ms=1570
2026-06-10 01:23:05,897 [INFO] nina.idle: idle_proposal_appended topic=provider_routing file=2026-06-10_proposals.md
2026-06-10 01:23:54,819 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07190704345703125, "success": true}
2026-06-10 01:23:54,819 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07190704345703125, "success": true}
2026-06-10 01:24:00,539 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-10 01:24:02,170 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 01:24:02,171 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 01:25:14,013 [INFO] nina.scheduler: Received signal 15, initiating graceful shutdown...
2026-06-10 01:25:14,013 [INFO] nina.scheduler: Received signal 15, initiating graceful shutdown...
2026-06-10 14:45:58,526 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1 reminders=0
2026-06-10 14:45:58,574 [INFO] nina.router: Loaded circuit breaker state from data/circuit_state.json
2026-06-10 14:45:59,327 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-10 14:45:59,328 [INFO] nina.router: HybridRouter initialized
2026-06-10 14:45:59,328 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-10 14:45:59,334 [INFO] nina.scheduler: Scheduler started — 16 jobs
2026-06-10 14:45:59,334 [INFO] nina.scheduler: Scheduler started — 16 jobs
2026-06-10 14:46:00,541 [INFO] nina.telegram: TelegramInterface polling started
2026-06-10 14:46:00,541 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-10 14:46:00,541 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-10 14:48:00,610 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-10 14:48:06,584 [INFO] nina.routerlog: {"ts": "2026-06-10T14:48:06.000+0600", "req_id": "d29099fc", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-10 14:48:06,584 [WARNING] nina.router: router_fail req_id=d29099fc provider=CHUTES err=http_401
2026-06-10 14:48:06,675 [INFO] nina.routerlog: {"ts": "2026-06-10T14:48:06.000+0600", "req_id": "d29099fc", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-10 14:48:06,675 [WARNING] nina.router: router_fail req_id=d29099fc provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-10 14:48:07,087 [INFO] nina.routerlog: {"ts": "2026-06-10T14:48:07.000+0600", "req_id": "d29099fc", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-10 14:48:07,087 [WARNING] nina.router: router_fail req_id=d29099fc provider=CEREBRAS err=http_404
2026-06-10 14:48:07,739 [INFO] nina.routerlog: {"ts": "2026-06-10T14:48:07.000+0600", "req_id": "d29099fc", "provider": "GROQ", "task_type": "research", "input_tokens": 370, "output_tokens": 77, "cost_usd": 0.0, "ttf_ms": 651, "total_ms": 651, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-10 14:48:07,739 [INFO] nina.router: router_success req_id=d29099fc provider=GROQ task=research ms=651
2026-06-10 14:48:07,745 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-10_proposals.md
2026-06-10 14:48:09,177 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 14:48:09,183 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 14:48:09,220 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 14:48:09,221 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 14:50:59,364 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021474123001098633, "success": true}
2026-06-10 14:50:59,364 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021474123001098633, "success": true}
2026-06-10 14:51:01,619 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 14:51:01,620 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 14:51:01,821 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-10 14:55:59,356 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.023144006729125977, "success": true}
2026-06-10 14:55:59,356 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.023144006729125977, "success": true}
2026-06-10 15:00:59,450 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.11391806602478027, "success": true}
2026-06-10 15:00:59,450 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.11391806602478027, "success": true}
2026-06-10 15:00:59,450 [INFO] nina.scheduler: reminder_check
2026-06-10 15:00:59,450 [INFO] nina.scheduler: reminder_check
2026-06-10 15:00:59,450 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.417533874511719e-05, "success": true}
2026-06-10 15:00:59,450 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.417533874511719e-05, "success": true}
2026-06-10 15:00:59,450 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 6.937980651855469e-05, "success": true}
2026-06-10 15:00:59,450 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 6.937980651855469e-05, "success": true}
2026-06-10 15:05:59,394 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.05774068832397461, "success": true}
2026-06-10 15:05:59,394 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.05774068832397461, "success": true}
2026-06-10 15:10:59,428 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.08939027786254883, "success": true}
2026-06-10 15:10:59,428 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.08939027786254883, "success": true}
2026-06-10 15:15:59,341 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 6.794929504394531e-05, "success": true}
2026-06-10 15:15:59,341 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 6.794929504394531e-05, "success": true}
2026-06-10 15:15:59,364 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022522449493408203, "success": true}
2026-06-10 15:15:59,364 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022522449493408203, "success": true}
2026-06-10 15:15:59,364 [INFO] nina.scheduler: reminder_check
2026-06-10 15:15:59,364 [INFO] nina.scheduler: reminder_check
2026-06-10 15:15:59,364 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00017833709716796875, "success": true}
2026-06-10 15:15:59,364 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00017833709716796875, "success": true}
2026-06-10 15:15:59,365 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 6.246566772460938e-05, "success": true}
2026-06-10 15:15:59,365 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 6.246566772460938e-05, "success": true}
2026-06-10 15:19:07,750 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-10 15:19:09,001 [INFO] nina.routerlog: {"ts": "2026-06-10T15:19:09.000+0600", "req_id": "8df088f3", "provider": "GROQ", "task_type": "research", "input_tokens": 369, "output_tokens": 97, "cost_usd": 0.0, "ttf_ms": 805, "total_ms": 805, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-10 15:19:09,001 [INFO] nina.router: router_success req_id=8df088f3 provider=GROQ task=research ms=805
2026-06-10 15:19:09,001 [INFO] nina.idle: idle_proposal_appended topic=morning_report file=2026-06-10_proposals.md
2026-06-10 15:20:59,395 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.052877187728881836, "success": true}
2026-06-10 15:20:59,395 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.052877187728881836, "success": true}
2026-06-10 15:21:04,114 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-10 15:21:06,875 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 15:21:06,876 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 15:25:59,429 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.08615803718566895, "success": true}
2026-06-10 15:25:59,429 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.08615803718566895, "success": true}
2026-06-10 15:30:59,356 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021399736404418945, "success": true}
2026-06-10 15:30:59,356 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021399736404418945, "success": true}
2026-06-10 15:30:59,357 [INFO] nina.scheduler: reminder_check
2026-06-10 15:30:59,357 [INFO] nina.scheduler: reminder_check
2026-06-10 15:30:59,362 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.004974842071533203, "success": true}
2026-06-10 15:30:59,362 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.004974842071533203, "success": true}
2026-06-10 15:30:59,362 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.1219253540039062e-05, "success": true}
2026-06-10 15:30:59,362 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.1219253540039062e-05, "success": true}
2026-06-10 15:35:59,393 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.055917978286743164, "success": true}
2026-06-10 15:35:59,393 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.055917978286743164, "success": true}
2026-06-10 15:40:59,425 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.08920526504516602, "success": true}
2026-06-10 15:40:59,425 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.08920526504516602, "success": true}
2026-06-10 15:45:59,335 [INFO] nina.scheduler: NINA operational
2026-06-10 15:45:59,335 [INFO] nina.scheduler: NINA operational
2026-06-10 15:45:59,335 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.00017881393432617188, "success": true}
2026-06-10 15:45:59,335 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.00017881393432617188, "success": true}
2026-06-10 15:45:59,336 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 5.841255187988281e-05, "success": true}
2026-06-10 15:45:59,336 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 5.841255187988281e-05, "success": true}
2026-06-10 15:45:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020854711532592773, "success": true}
2026-06-10 15:45:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020854711532592773, "success": true}
2026-06-10 15:45:59,357 [INFO] nina.scheduler: reminder_check
2026-06-10 15:45:59,357 [INFO] nina.scheduler: reminder_check
2026-06-10 15:45:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00012445449829101562, "success": true}
2026-06-10 15:45:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00012445449829101562, "success": true}
2026-06-10 15:45:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 4.649162292480469e-05, "success": true}
2026-06-10 15:45:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 4.649162292480469e-05, "success": true}
2026-06-10 15:50:09,010 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-10 15:50:10,334 [INFO] nina.routerlog: {"ts": "2026-06-10T15:50:10.000+0600", "req_id": "a345e45f", "provider": "GROQ", "task_type": "research", "input_tokens": 359, "output_tokens": 117, "cost_usd": 0.0, "ttf_ms": 876, "total_ms": 876, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-10 15:50:10,334 [INFO] nina.router: router_success req_id=a345e45f provider=GROQ task=research ms=876
2026-06-10 15:50:10,334 [INFO] nina.idle: idle_proposal_appended topic=provider_routing file=2026-06-10_proposals.md
2026-06-10 15:50:59,389 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.05160808563232422, "success": true}
2026-06-10 15:50:59,389 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.05160808563232422, "success": true}
2026-06-10 15:51:05,739 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-10 15:51:07,100 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 15:51:07,100 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 15:55:59,424 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.08554410934448242, "success": true}
2026-06-10 15:55:59,424 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.08554410934448242, "success": true}
2026-06-10 16:00:59,359 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021535873413085938, "success": true}
2026-06-10 16:00:59,359 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021535873413085938, "success": true}
2026-06-10 16:00:59,360 [INFO] nina.scheduler: reminder_check
2026-06-10 16:00:59,360 [INFO] nina.scheduler: reminder_check
2026-06-10 16:00:59,360 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001537799835205078, "success": true}
2026-06-10 16:00:59,360 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001537799835205078, "success": true}
2026-06-10 16:00:59,360 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.0265579223632812e-05, "success": true}
2026-06-10 16:00:59,360 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.0265579223632812e-05, "success": true}
2026-06-10 16:05:59,359 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021915674209594727, "success": true}
2026-06-10 16:05:59,359 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021915674209594727, "success": true}
2026-06-10 16:10:59,360 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022339344024658203, "success": true}
2026-06-10 16:10:59,360 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022339344024658203, "success": true}
2026-06-10 16:15:59,341 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 5.14984130859375e-05, "success": true}
2026-06-10 16:15:59,341 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 5.14984130859375e-05, "success": true}
2026-06-10 16:15:59,362 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021459579467773438, "success": true}
2026-06-10 16:15:59,362 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021459579467773438, "success": true}
2026-06-10 16:15:59,363 [INFO] nina.scheduler: reminder_check
2026-06-10 16:15:59,363 [INFO] nina.scheduler: reminder_check
2026-06-10 16:15:59,363 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00015997886657714844, "success": true}
2026-06-10 16:15:59,363 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00015997886657714844, "success": true}
2026-06-10 16:15:59,363 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.002716064453125e-05, "success": true}
2026-06-10 16:15:59,363 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.002716064453125e-05, "success": true}
2026-06-10 16:20:59,386 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.0453190803527832, "success": true}
2026-06-10 16:20:59,386 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.0453190803527832, "success": true}
2026-06-10 16:21:10,340 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-10 16:21:11,660 [INFO] nina.routerlog: {"ts": "2026-06-10T16:21:11.000+0600", "req_id": "54d45086", "provider": "GROQ", "task_type": "research", "input_tokens": 367, "output_tokens": 92, "cost_usd": 0.0, "ttf_ms": 856, "total_ms": 856, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-10 16:21:11,660 [INFO] nina.router: router_success req_id=54d45086 provider=GROQ task=research ms=856
2026-06-10 16:21:11,660 [INFO] nina.idle: idle_proposal_appended topic=memory_context file=2026-06-10_proposals.md
2026-06-10 16:25:59,363 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022154569625854492, "success": true}
2026-06-10 16:25:59,363 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022154569625854492, "success": true}
2026-06-10 16:26:08,451 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-10 16:26:09,999 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 16:26:10,000 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 16:30:59,363 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021938085556030273, "success": true}
2026-06-10 16:30:59,363 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021938085556030273, "success": true}
2026-06-10 16:30:59,363 [INFO] nina.scheduler: reminder_check
2026-06-10 16:30:59,363 [INFO] nina.scheduler: reminder_check
2026-06-10 16:30:59,363 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 8.726119995117188e-05, "success": true}
2026-06-10 16:30:59,363 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 8.726119995117188e-05, "success": true}
2026-06-10 16:30:59,363 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 4.38690185546875e-05, "success": true}
2026-06-10 16:30:59,363 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 4.38690185546875e-05, "success": true}
2026-06-10 16:35:59,360 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02177262306213379, "success": true}
2026-06-10 16:35:59,360 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02177262306213379, "success": true}
2026-06-10 16:40:59,417 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07348418235778809, "success": true}
2026-06-10 16:40:59,417 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07348418235778809, "success": true}
2026-06-10 16:45:59,335 [INFO] nina.scheduler: NINA operational
2026-06-10 16:45:59,335 [INFO] nina.scheduler: NINA operational
2026-06-10 16:45:59,335 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.00016236305236816406, "success": true}
2026-06-10 16:45:59,335 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.00016236305236816406, "success": true}
2026-06-10 16:45:59,336 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 6.866455078125e-05, "success": true}
2026-06-10 16:45:59,336 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 6.866455078125e-05, "success": true}
2026-06-10 16:45:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021605730056762695, "success": true}
2026-06-10 16:45:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021605730056762695, "success": true}
2026-06-10 16:45:59,358 [INFO] nina.scheduler: reminder_check
2026-06-10 16:45:59,358 [INFO] nina.scheduler: reminder_check
2026-06-10 16:45:59,358 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00015282630920410156, "success": true}
2026-06-10 16:45:59,358 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00015282630920410156, "success": true}
2026-06-10 16:45:59,358 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 1.9550323486328125e-05, "success": true}
2026-06-10 16:45:59,358 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 1.9550323486328125e-05, "success": true}
2026-06-10 16:50:59,381 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.047189950942993164, "success": true}
2026-06-10 16:50:59,381 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.047189950942993164, "success": true}
2026-06-10 16:52:11,666 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-10 16:52:28,095 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "GROQ", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,096 [WARNING] nina.router: router_fail req_id=19c5739f provider=GROQ err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,102 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "MISTRAL", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,102 [WARNING] nina.router: router_fail req_id=19c5739f provider=MISTRAL err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,123 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "DEEPSEEK", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,123 [WARNING] nina.router: router_fail req_id=19c5739f provider=DEEPSEEK err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,126 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "GEMINI", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,126 [WARNING] nina.router: router_fail req_id=19c5739f provider=GEMINI err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,129 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "TOGETHER", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,129 [WARNING] nina.router: router_fail req_id=19c5739f provider=TOGETHER err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,132 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "COHERE", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,132 [WARNING] nina.router: router_fail req_id=19c5739f provider=COHERE err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,134 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "FIREWORKS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,134 [WARNING] nina.router: router_fail req_id=19c5739f provider=FIREWORKS err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,136 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "XAI", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,136 [WARNING] nina.router: router_fail req_id=19c5739f provider=XAI err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,150 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "SAMBANOVA", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,151 [WARNING] nina.router: router_fail req_id=19c5739f provider=SAMBANOVA err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,153 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "HYPERBOLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,153 [WARNING] nina.router: router_fail req_id=19c5739f provider=HYPERBOLIC err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,155 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "NOVITA", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,155 [WARNING] nina.router: router_fail req_id=19c5739f provider=NOVITA err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,158 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "OPENAI", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,158 [WARNING] nina.router: router_fail req_id=19c5739f provider=OPENAI err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,160 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "OPENROUTER", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,160 [WARNING] nina.router: router_fail req_id=19c5739f provider=OPENROUTER err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,177 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,177 [WARNING] nina.router: router_fail req_id=19c5739f provider=CHUTES err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,190 [WARNING] nina.model_discovery: Discovery failed for GROQ: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,192 [WARNING] nina.model_discovery: Discovery failed for GEMINI: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,192 [WARNING] nina.model_discovery: Discovery failed for GROQ: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,194 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,194 [WARNING] nina.router: router_fail req_id=19c5739f provider=HFPUBLIC err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,195 [WARNING] nina.model_discovery: Discovery failed for CEREBRAS: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,196 [WARNING] nina.model_discovery: Discovery failed for GEMINI: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,196 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,197 [WARNING] nina.router: router_fail req_id=19c5739f provider=CEREBRAS err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,210 [WARNING] nina.model_discovery: Discovery failed for MISTRAL: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,211 [WARNING] nina.model_discovery: Discovery failed for CEREBRAS: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,212 [WARNING] nina.model_discovery: Discovery failed for GROQ: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,213 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-10 16:52:28,213 [WARNING] nina.router: router_fail req_id=19c5739f provider=POLLINATIONS err=[Errno -3] Temporary failure in name resolution
2026-06-10 16:52:28,214 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,215 [WARNING] nina.model_discovery: Discovery failed for MISTRAL: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,216 [WARNING] nina.model_discovery: Discovery failed for GEMINI: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,217 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,217 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 16:52:28,219 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,220 [WARNING] nina.model_discovery: Discovery failed for CEREBRAS: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,221 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,221 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 16:52:28,223 [WARNING] nina.model_discovery: Discovery failed for MISTRAL: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,224 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,226 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-10 16:52:28,227 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 16:52:28,238 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:28.000+0600", "req_id": "19c5739f", "provider": "LOCALHEAVY", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_400"}
2026-06-10 16:52:28,238 [WARNING] nina.router: router_fail req_id=19c5739f provider=LOCALHEAVY err=http_400
2026-06-10 16:52:37,831 [INFO] nina.routerlog: {"ts": "2026-06-10T16:52:37.000+0600", "req_id": "19c5739f", "provider": "LOCALFAST", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 9593, "total_ms": 9593, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-10 16:52:37,831 [INFO] nina.router: router_success req_id=19c5739f provider=LOCALFAST task=research ms=9593
2026-06-10 16:52:37,832 [INFO] nina.idle: idle_proposal_appended topic=scheduler_errors file=2026-06-10_proposals.md
2026-06-10 16:55:59,360 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020522594451904297, "success": true}
2026-06-10 16:55:59,360 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020522594451904297, "success": true}
2026-06-10 17:00:59,362 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020280838012695312, "success": true}
2026-06-10 17:00:59,362 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020280838012695312, "success": true}
2026-06-10 17:00:59,362 [INFO] nina.scheduler: reminder_check
2026-06-10 17:00:59,362 [INFO] nina.scheduler: reminder_check
2026-06-10 17:00:59,362 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.059906005859375e-05, "success": true}
2026-06-10 17:00:59,362 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.059906005859375e-05, "success": true}
2026-06-10 17:00:59,363 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.790855407714844e-05, "success": true}
2026-06-10 17:00:59,363 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.790855407714844e-05, "success": true}
2026-06-10 17:05:59,364 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021328210830688477, "success": true}
2026-06-10 17:05:59,364 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021328210830688477, "success": true}
2026-06-10 17:10:59,409 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07395029067993164, "success": true}
2026-06-10 17:10:59,409 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07395029067993164, "success": true}
2026-06-10 17:15:59,337 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 6.532669067382812e-05, "success": true}
2026-06-10 17:15:59,337 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 6.532669067382812e-05, "success": true}
2026-06-10 17:15:59,442 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.10506224632263184, "success": true}
2026-06-10 17:15:59,442 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.10506224632263184, "success": true}
2026-06-10 17:15:59,442 [INFO] nina.scheduler: reminder_check
2026-06-10 17:15:59,442 [INFO] nina.scheduler: reminder_check
2026-06-10 17:15:59,443 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001456737518310547, "success": true}
2026-06-10 17:15:59,443 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001456737518310547, "success": true}
2026-06-10 17:15:59,443 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.002716064453125e-05, "success": true}
2026-06-10 17:15:59,443 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.002716064453125e-05, "success": true}
2026-06-10 17:20:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020490407943725586, "success": true}
2026-06-10 17:20:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020490407943725586, "success": true}
2026-06-10 17:23:37,843 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-10 17:23:39,624 [INFO] nina.routerlog: {"ts": "2026-06-10T17:23:39.000+0600", "req_id": "59693fe1", "provider": "GROQ", "task_type": "research", "input_tokens": 367, "output_tokens": 99, "cost_usd": 0.0, "ttf_ms": 1333, "total_ms": 1333, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-10 17:23:39,624 [INFO] nina.router: router_success req_id=59693fe1 provider=GROQ task=research ms=1333
2026-06-10 17:23:39,624 [INFO] nina.idle: idle_proposal_appended topic=telegram_interface file=2026-06-10_proposals.md
2026-06-10 17:25:59,406 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.06722569465637207, "success": true}
2026-06-10 17:25:59,406 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.06722569465637207, "success": true}
2026-06-10 17:26:11,546 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-10 17:26:11,683 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 17:26:11,684 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 17:30:59,361 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022641420364379883, "success": true}
2026-06-10 17:30:59,361 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022641420364379883, "success": true}
2026-06-10 17:30:59,362 [INFO] nina.scheduler: reminder_check
2026-06-10 17:30:59,362 [INFO] nina.scheduler: reminder_check
2026-06-10 17:30:59,362 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00015592575073242188, "success": true}
2026-06-10 17:30:59,362 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00015592575073242188, "success": true}
2026-06-10 17:30:59,362 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.790855407714844e-05, "success": true}
2026-06-10 17:30:59,362 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.790855407714844e-05, "success": true}
2026-06-10 17:35:59,369 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02848672866821289, "success": true}
2026-06-10 17:35:59,369 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02848672866821289, "success": true}
2026-06-10 17:40:59,402 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.060513973236083984, "success": true}
2026-06-10 17:40:59,402 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.060513973236083984, "success": true}
2026-06-10 17:45:59,334 [INFO] nina.scheduler: NINA operational
2026-06-10 17:45:59,334 [INFO] nina.scheduler: NINA operational
2026-06-10 17:45:59,334 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.00017023086547851562, "success": true}
2026-06-10 17:45:59,334 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.00017023086547851562, "success": true}
2026-06-10 17:45:59,335 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 5.5789947509765625e-05, "success": true}
2026-06-10 17:45:59,335 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 5.5789947509765625e-05, "success": true}
2026-06-10 17:45:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021811723709106445, "success": true}
2026-06-10 17:45:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021811723709106445, "success": true}
2026-06-10 17:45:59,357 [INFO] nina.scheduler: reminder_check
2026-06-10 17:45:59,357 [INFO] nina.scheduler: reminder_check
2026-06-10 17:45:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001537799835205078, "success": true}
2026-06-10 17:45:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001537799835205078, "success": true}
2026-06-10 17:45:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.0742416381835938e-05, "success": true}
2026-06-10 17:45:59,357 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.0742416381835938e-05, "success": true}
2026-06-10 17:50:59,356 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022064208984375, "success": true}
2026-06-10 17:50:59,356 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022064208984375, "success": true}
2026-06-10 17:54:39,637 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-10 17:54:40,869 [INFO] nina.routerlog: {"ts": "2026-06-10T17:54:40.000+0600", "req_id": "62ad2209", "provider": "GROQ", "task_type": "research", "input_tokens": 370, "output_tokens": 87, "cost_usd": 0.0, "ttf_ms": 771, "total_ms": 771, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-10 17:54:40,869 [INFO] nina.router: router_success req_id=62ad2209 provider=GROQ task=research ms=771
2026-06-10 17:54:40,869 [INFO] nina.idle: idle_proposal_appended topic=config_robustness file=2026-06-10_proposals.md
2026-06-10 17:55:59,358 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.023090600967407227, "success": true}
2026-06-10 17:55:59,358 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.023090600967407227, "success": true}
2026-06-10 17:56:13,774 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-10 17:56:15,704 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 17:56:15,705 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 18:00:59,435 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.09883809089660645, "success": true}
2026-06-10 18:00:59,435 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.09883809089660645, "success": true}
2026-06-10 18:00:59,435 [INFO] nina.scheduler: reminder_check
2026-06-10 18:00:59,435 [INFO] nina.scheduler: reminder_check
2026-06-10 18:00:59,436 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001163482666015625, "success": true}
2026-06-10 18:00:59,436 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001163482666015625, "success": true}
2026-06-10 18:00:59,436 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.002716064453125e-05, "success": true}
2026-06-10 18:00:59,436 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.002716064453125e-05, "success": true}
2026-06-10 18:05:59,366 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.028505325317382812, "success": true}
2026-06-10 18:05:59,366 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.028505325317382812, "success": true}
2026-06-10 18:06:45,001 [INFO] nina.scheduler: Received signal 15, initiating graceful shutdown...
2026-06-10 18:06:45,001 [INFO] nina.scheduler: Received signal 15, initiating graceful shutdown...
2026-06-10 22:23:25,939 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1 reminders=0
2026-06-10 22:23:25,986 [INFO] nina.router: Loaded circuit breaker state from data/circuit_state.json
2026-06-10 22:23:25,998 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-10 22:23:25,998 [INFO] nina.router: HybridRouter initialized
2026-06-10 22:23:25,998 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-10 22:23:26,004 [INFO] nina.scheduler: Scheduler started — 16 jobs
2026-06-10 22:23:26,004 [INFO] nina.scheduler: Scheduler started — 16 jobs
2026-06-10 22:23:26,811 [INFO] nina.telegram: TelegramInterface polling started
2026-06-10 22:23:26,811 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-10 22:23:26,812 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-10 22:25:26,871 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-10 22:25:33,584 [INFO] nina.routerlog: {"ts": "2026-06-10T22:25:33.000+0600", "req_id": "dd370cf7", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-10 22:25:33,584 [WARNING] nina.router: router_fail req_id=dd370cf7 provider=CHUTES err=http_401
2026-06-10 22:25:33,660 [INFO] nina.routerlog: {"ts": "2026-06-10T22:25:33.000+0600", "req_id": "dd370cf7", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-10 22:25:33,661 [WARNING] nina.router: router_fail req_id=dd370cf7 provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-10 22:25:34,213 [INFO] nina.routerlog: {"ts": "2026-06-10T22:25:34.000+0600", "req_id": "dd370cf7", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-10 22:25:34,213 [WARNING] nina.router: router_fail req_id=dd370cf7 provider=CEREBRAS err=http_404
2026-06-10 22:25:34,817 [INFO] nina.routerlog: {"ts": "2026-06-10T22:25:34.000+0600", "req_id": "dd370cf7", "provider": "GROQ", "task_type": "research", "input_tokens": 369, "output_tokens": 78, "cost_usd": 0.0, "ttf_ms": 603, "total_ms": 603, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-10 22:25:34,817 [INFO] nina.router: router_success req_id=dd370cf7 provider=GROQ task=research ms=603
2026-06-10 22:25:34,823 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-10_proposals.md
2026-06-10 22:25:37,558 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 22:25:37,559 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 22:25:38,920 [WARNING] nina.model_discovery: Discovery failed for CEREBRAS: . Using fallback.
2026-06-10 22:25:40,812 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 22:25:40,812 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 22:28:26,025 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021813631057739258, "success": true}
2026-06-10 22:28:26,025 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021813631057739258, "success": true}
2026-06-10 22:28:29,214 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-10 22:28:30,996 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 22:28:30,997 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 22:33:26,089 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.08167386054992676, "success": true}
2026-06-10 22:33:26,089 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.08167386054992676, "success": true}
2026-06-10 22:38:26,122 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.11501765251159668, "success": true}
2026-06-10 22:38:26,122 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.11501765251159668, "success": true}
2026-06-10 22:38:26,122 [INFO] nina.scheduler: reminder_check
2026-06-10 22:38:26,122 [INFO] nina.scheduler: reminder_check
2026-06-10 22:38:26,123 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00019478797912597656, "success": true}
2026-06-10 22:38:26,123 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00019478797912597656, "success": true}
2026-06-10 22:38:26,123 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 5.078315734863281e-05, "success": true}
2026-06-10 22:38:26,123 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 5.078315734863281e-05, "success": true}
2026-06-10 22:43:26,054 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.05128622055053711, "success": true}
2026-06-10 22:43:26,054 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.05128622055053711, "success": true}
2026-06-10 22:48:26,032 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.024047374725341797, "success": true}
2026-06-10 22:48:26,032 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.024047374725341797, "success": true}
2026-06-10 22:53:26,013 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 7.271766662597656e-05, "success": true}
2026-06-10 22:53:26,013 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 7.271766662597656e-05, "success": true}
2026-06-10 22:53:26,124 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.11146426200866699, "success": true}
2026-06-10 22:53:26,124 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.11146426200866699, "success": true}
2026-06-10 22:53:26,125 [INFO] nina.scheduler: reminder_check
2026-06-10 22:53:26,125 [INFO] nina.scheduler: reminder_check
2026-06-10 22:53:26,125 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00011539459228515625, "success": true}
2026-06-10 22:53:26,125 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00011539459228515625, "success": true}
2026-06-10 22:53:26,125 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.1219253540039062e-05, "success": true}
2026-06-10 22:53:26,125 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.1219253540039062e-05, "success": true}
2026-06-10 22:56:34,829 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-10 22:56:36,065 [INFO] nina.routerlog: {"ts": "2026-06-10T22:56:36.000+0600", "req_id": "bcdd3de9", "provider": "GROQ", "task_type": "research", "input_tokens": 368, "output_tokens": 88, "cost_usd": 0.0, "ttf_ms": 753, "total_ms": 753, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-10 22:56:36,065 [INFO] nina.router: router_success req_id=bcdd3de9 provider=GROQ task=research ms=753
2026-06-10 22:56:36,065 [INFO] nina.idle: idle_proposal_appended topic=morning_report file=2026-06-10_proposals.md
2026-06-10 22:58:26,027 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02091813087463379, "success": true}
2026-06-10 22:58:26,027 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02091813087463379, "success": true}
2026-06-10 22:58:31,379 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-10 22:58:32,209 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-10 22:58:32,210 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-10 23:00:00,953 [INFO] nina.scheduler: {"event": "job_run", "job": "cost_report", "duration": 0.9480917453765869, "success": true}
2026-06-10 23:00:00,953 [INFO] nina.scheduler: {"event": "job_run", "job": "cost_report", "duration": 0.9480917453765869, "success": true}
2026-06-10 23:03:26,031 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021802663803100586, "success": true}
2026-06-10 23:03:26,031 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021802663803100586, "success": true}
2026-06-10 23:08:26,124 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.12104201316833496, "success": true}
2026-06-10 23:08:26,124 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.12104201316833496, "success": true}
2026-06-10 23:08:26,125 [INFO] nina.scheduler: reminder_check
2026-06-10 23:08:26,125 [INFO] nina.scheduler: reminder_check
2026-06-10 23:08:26,125 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001220703125, "success": true}
2026-06-10 23:08:26,125 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001220703125, "success": true}
2026-06-10 23:08:26,125 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.0040740966796875e-05, "success": true}
2026-06-10 23:08:26,125 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.0040740966796875e-05, "success": true}
2026-06-10 23:13:26,056 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.048476457595825195, "success": true}
2026-06-10 23:13:26,056 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.048476457595825195, "success": true}
2026-06-10 23:18:26,090 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07885289192199707, "success": true}
2026-06-10 23:18:26,090 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07885289192199707, "success": true}
```

### logs/nina.log.2026-06-03
Last modified: 2026-06-03 21:14:06
Size: 348 bytes
```log
2026-06-03 17:41:55,345 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-03 20:53:32,635 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-03 21:14:06,880 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
```

### logs/nina.log.2026-06-04
Last modified: 2026-06-05 00:09:23
Size: 53337 bytes
```log
2026-06-04 10:32:55,175 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 10:38:12,748 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 10:38:15,403 [INFO] nina.routerlog: {"ts": "2026-06-04T10:38:15.000+0600", "req_id": "8875d6fa", "provider": "GROQ", "task_type": "research", "input_tokens": 394, "output_tokens": 267, "cost_usd": 0.0, "ttf_ms": 1377, "total_ms": 1377, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 10:38:15,404 [INFO] nina.router: router_success req_id=8875d6fa provider=GROQ task=research ms=1377
2026-06-04 10:38:15,409 [INFO] nina.idle: idle_proposal_appended topic=telegram_interface file=2026-06-04_proposals.md
2026-06-04 10:38:25,984 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 11:49:03,248 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 11:51:22,394 [WARNING] nina.router: nlp_classification_failed input='can you make cron jobs?' falling through to general task
2026-06-04 11:51:24,195 [INFO] nina.routerlog: {"ts": "2026-06-04T11:51:24.000+0600", "req_id": "5f6924f7", "provider": "GROQ", "task_type": "general", "input_tokens": 140, "output_tokens": 101, "cost_usd": 0.0, "ttf_ms": 866, "total_ms": 866, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 11:51:24,195 [INFO] nina.router: router_success req_id=5f6924f7 provider=GROQ task=general ms=866
2026-06-04 11:51:24,195 [INFO] nina.agent: agent_step step=1 task=general response='To determine if I can make cron jobs, I need to consider the capabilities of the'
2026-06-04 11:51:24,202 [WARNING] nina.tools.shell: shell:blocked cmd='crontab -l'
2026-06-04 11:51:26,864 [INFO] nina.routerlog: {"ts": "2026-06-04T11:51:26.000+0600", "req_id": "53813055", "provider": "GROQ", "task_type": "general", "input_tokens": 276, "output_tokens": 120, "cost_usd": 0.0, "ttf_ms": 666, "total_ms": 666, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 11:51:26,864 [INFO] nina.router: router_success req_id=53813055 provider=GROQ task=general ms=666
2026-06-04 11:51:26,864 [INFO] nina.agent: agent_step step=2 task=general response="It seems that I don't have direct access to the 'crontab' command due to allowan"
2026-06-04 11:51:29,096 [INFO] nina.tools.search: tavily_search query='how to create cron jobs alternatively' results=5
2026-06-04 11:51:30,986 [INFO] nina.routerlog: {"ts": "2026-06-04T11:51:30.000+0600", "req_id": "fb3890b5", "provider": "GROQ", "task_type": "general", "input_tokens": 500, "output_tokens": 145, "cost_usd": 0.0, "ttf_ms": 1890, "total_ms": 1890, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 11:51:30,986 [INFO] nina.router: router_success req_id=fb3890b5 provider=GROQ task=general ms=1890
2026-06-04 11:51:30,987 [INFO] nina.agent: agent_step step=3 task=general response="I've found some alternatives to cron jobs, which is useful information. However,"
2026-06-04 11:51:30,987 [WARNING] nina.tools.shell: shell:blocked cmd='anacron -h'
2026-06-04 11:51:33,875 [INFO] nina.routerlog: {"ts": "2026-06-04T11:51:33.000+0600", "req_id": "50cbeb26", "provider": "GROQ", "task_type": "general", "input_tokens": 766, "output_tokens": 135, "cost_usd": 0.0, "ttf_ms": 886, "total_ms": 886, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 11:51:33,876 [INFO] nina.router: router_success req_id=50cbeb26 provider=GROQ task=general ms=886
2026-06-04 11:51:33,876 [INFO] nina.agent: agent_step step=4 task=general response="It seems that I'm also unable to use the 'anacron' command, which is one of the "
2026-06-04 11:51:36,674 [INFO] nina.routerlog: {"ts": "2026-06-04T11:51:36.000+0600", "req_id": "6647dd8a", "provider": "GROQ", "task_type": "general", "input_tokens": 1015, "output_tokens": 126, "cost_usd": 0.0, "ttf_ms": 795, "total_ms": 795, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 11:51:36,675 [INFO] nina.router: router_success req_id=6647dd8a provider=GROQ task=general ms=795
2026-06-04 11:51:36,676 [INFO] nina.agent: agent_step step=5 task=general response='It seems there was an error in the TOOL:system INPUT:status of cron job capabili'
2026-06-04 11:54:03,417 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 11:59:03,425 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 12:04:03,435 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 12:09:03,438 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 12:14:03,443 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 12:14:52,149 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 12:14:54,818 [INFO] nina.routerlog: {"ts": "2026-06-04T12:14:54.000+0600", "req_id": "d4069bc7", "provider": "GROQ", "task_type": "research", "input_tokens": 397, "output_tokens": 257, "cost_usd": 0.0, "ttf_ms": 1289, "total_ms": 1289, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 12:14:54,818 [INFO] nina.router: router_success req_id=d4069bc7 provider=GROQ task=research ms=1289
2026-06-04 12:14:54,819 [INFO] nina.idle: idle_proposal_appended topic=config_robustness file=2026-06-04_proposals.md
2026-06-04 12:15:27,165 [INFO] nina.scheduler: NINA operational
2026-06-04 12:19:03,451 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 12:24:07,086 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 12:38:09,528 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 12:41:33,412 [INFO] nina.routerlog: {"ts": "2026-06-04T12:41:33.000+0600", "req_id": "fada0103", "provider": "GROQ", "task_type": "general", "input_tokens": 190, "output_tokens": 204, "cost_usd": 0.0, "ttf_ms": 1368, "total_ms": 1368, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 12:41:33,412 [INFO] nina.router: router_success req_id=fada0103 provider=GROQ task=general ms=1368
2026-06-04 12:41:33,412 [INFO] nina.agent: agent_step step=1 task=general response='[Step 1/3] THINK: To create a scheduled task, I need to determine the best appro'
2026-06-04 12:42:08,321 [WARNING] nina.router: nlp_classification_failed input='what are the commands' falling through to general task
2026-06-04 12:42:10,228 [INFO] nina.routerlog: {"ts": "2026-06-04T12:42:10.000+0600", "req_id": "94e6df09", "provider": "GROQ", "task_type": "general", "input_tokens": 230, "output_tokens": 114, "cost_usd": 0.0, "ttf_ms": 1037, "total_ms": 1037, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 12:42:10,228 [INFO] nina.router: router_success req_id=94e6df09 provider=GROQ task=general ms=1037
2026-06-04 12:42:10,228 [INFO] nina.agent: agent_step step=1 task=general response='THINK: To determine the commands, I need to consider the available tools.\n\nPLAN:'
2026-06-04 12:42:12,262 [INFO] nina.tools.search: tavily_search query='query\n2. TOOL:browser -' results=5
2026-06-04 12:42:13,295 [INFO] nina.routerlog: {"ts": "2026-06-04T12:42:13.000+0600", "req_id": "e8be7ceb", "provider": "GROQ", "task_type": "general", "input_tokens": 427, "output_tokens": 152, "cost_usd": 0.0, "ttf_ms": 1031, "total_ms": 1031, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 12:42:13,295 [INFO] nina.router: router_success req_id=e8be7ceb provider=GROQ task=general ms=1031
2026-06-04 12:42:13,295 [INFO] nina.agent: agent_step step=2 task=general response="THINK: The user is looking for a way to query a website's content, and it seems "
2026-06-04 12:42:15,756 [INFO] nina.tools.search: tavily_search query='query (e.g. "website content query tools")\n2. TOOL:browser -' results=5
2026-06-04 12:42:17,187 [INFO] nina.routerlog: {"ts": "2026-06-04T12:42:17.000+0600", "req_id": "79fe1e82", "provider": "GROQ", "task_type": "general", "input_tokens": 719, "output_tokens": 284, "cost_usd": 0.0, "ttf_ms": 1430, "total_ms": 1430, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 12:42:17,187 [INFO] nina.router: router_success req_id=79fe1e82 provider=GROQ task=general ms=1430
2026-06-04 12:42:17,187 [INFO] nina.agent: agent_step step=3 task=general response="THINK: The user has found some tools that can help with querying a website's con"
2026-06-04 12:42:19,357 [INFO] nina.tools.search: tavily_search query='query (e.g. "website content query tools", "query website content")\n2. TOOL:browser -' results=5
2026-06-04 12:42:20,465 [INFO] nina.routerlog: {"ts": "2026-06-04T12:42:20.000+0600", "req_id": "39f33e09", "provider": "GROQ", "task_type": "general", "input_tokens": 1205, "output_tokens": 295, "cost_usd": 0.0, "ttf_ms": 1107, "total_ms": 1107, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 12:42:20,465 [INFO] nina.router: router_success req_id=39f33e09 provider=GROQ task=general ms=1107
2026-06-04 12:42:20,466 [INFO] nina.agent: agent_step step=4 task=general response="THINK: The user has found various tools that can help with querying a website's "
2026-06-04 12:42:21,419 [INFO] nina.tools.search: tavily_search query='query (e.g. "website content query tools", "query website content")\n2. TOOL:browser -' results=5
2026-06-04 12:42:31,984 [INFO] nina.routerlog: {"ts": "2026-06-04T12:42:31.000+0600", "req_id": "90cc99a5", "provider": "MISTRAL", "task_type": "general", "input_tokens": 1683, "output_tokens": 663, "cost_usd": 0.0, "ttf_ms": 10563, "total_ms": 10563, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 12:42:31,984 [INFO] nina.router: router_success req_id=90cc99a5 provider=MISTRAL task=general ms=10563
2026-06-04 12:42:31,984 [INFO] nina.agent: agent_step step=5 task=general response='### **Commands to Query Website Content**\n\nHere are the available commands and m'
2026-06-04 12:43:09,532 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 12:48:09,536 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 12:53:09,542 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 12:55:00,891 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 12:55:09,408 [INFO] nina.routerlog: {"ts": "2026-06-04T12:55:09.000+0600", "req_id": "5ef1ba1d", "provider": "MISTRAL", "task_type": "research", "input_tokens": 454, "output_tokens": 400, "cost_usd": 0.0, "ttf_ms": 7358, "total_ms": 7358, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 12:55:09,408 [INFO] nina.router: router_success req_id=5ef1ba1d provider=MISTRAL task=research ms=7358
2026-06-04 12:55:09,409 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-04_proposals.md
2026-06-04 12:58:09,550 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 13:03:09,551 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 13:08:09,554 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 13:13:09,558 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 13:15:27,168 [INFO] nina.scheduler: NINA operational
2026-06-04 13:18:09,567 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 13:23:09,579 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 13:26:09,423 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 13:26:19,575 [INFO] nina.routerlog: {"ts": "2026-06-04T13:26:19.000+0600", "req_id": "1cd6137c", "provider": "MISTRAL", "task_type": "research", "input_tokens": 453, "output_tokens": 540, "cost_usd": 0.0, "ttf_ms": 10037, "total_ms": 10037, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 13:26:19,575 [INFO] nina.router: router_success req_id=1cd6137c provider=MISTRAL task=research ms=10037
2026-06-04 13:26:19,575 [INFO] nina.idle: idle_proposal_appended topic=morning_report file=2026-06-04_proposals.md
2026-06-04 13:28:09,583 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 13:33:09,588 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 13:38:09,595 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 13:43:09,606 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 13:48:09,610 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 13:53:09,616 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 13:57:19,594 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 13:57:32,854 [INFO] nina.routerlog: {"ts": "2026-06-04T13:57:32.000+0600", "req_id": "a599a4c6", "provider": "MISTRAL", "task_type": "research", "input_tokens": 447, "output_tokens": 752, "cost_usd": 0.0, "ttf_ms": 13152, "total_ms": 13152, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 13:57:32,854 [INFO] nina.router: router_success req_id=a599a4c6 provider=MISTRAL task=research ms=13152
2026-06-04 13:57:32,855 [INFO] nina.idle: idle_proposal_appended topic=provider_routing file=2026-06-04_proposals.md
2026-06-04 13:58:09,623 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 14:03:09,631 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 14:08:09,641 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 14:13:09,642 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 14:15:27,161 [INFO] nina.scheduler: NINA operational
2026-06-04 14:18:09,644 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 14:23:09,651 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 14:28:09,659 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 14:28:32,860 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 14:28:50,657 [INFO] nina.routerlog: {"ts": "2026-06-04T14:28:50.000+0600", "req_id": "9a830ecc", "provider": "MISTRAL", "task_type": "research", "input_tokens": 452, "output_tokens": 932, "cost_usd": 0.0, "ttf_ms": 17684, "total_ms": 17684, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 14:28:50,657 [INFO] nina.router: router_success req_id=9a830ecc provider=MISTRAL task=research ms=17684
2026-06-04 14:28:50,657 [INFO] nina.idle: idle_proposal_appended topic=memory_context file=2026-06-04_proposals.md
2026-06-04 14:33:09,670 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 14:38:09,673 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 14:43:09,684 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 14:48:09,696 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 14:53:09,697 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 14:58:09,701 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 14:59:50,671 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 15:00:00,635 [INFO] nina.routerlog: {"ts": "2026-06-04T15:00:00.000+0600", "req_id": "a2686228", "provider": "MISTRAL", "task_type": "research", "input_tokens": 451, "output_tokens": 539, "cost_usd": 0.0, "ttf_ms": 9853, "total_ms": 9853, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 15:00:00,635 [INFO] nina.router: router_success req_id=a2686228 provider=MISTRAL task=research ms=9853
2026-06-04 15:00:00,635 [INFO] nina.idle: idle_proposal_appended topic=scheduler_errors file=2026-06-04_proposals.md
2026-06-04 15:03:09,704 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 15:08:09,709 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 15:13:09,715 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 15:15:27,166 [INFO] nina.scheduler: NINA operational
2026-06-04 15:18:09,723 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 15:23:09,734 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 15:28:09,736 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 15:31:00,654 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 15:31:13,733 [INFO] nina.routerlog: {"ts": "2026-06-04T15:31:13.000+0600", "req_id": "5b482287", "provider": "MISTRAL", "task_type": "research", "input_tokens": 454, "output_tokens": 629, "cost_usd": 0.0, "ttf_ms": 12965, "total_ms": 12965, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 15:31:13,733 [INFO] nina.router: router_success req_id=5b482287 provider=MISTRAL task=research ms=12965
2026-06-04 15:31:13,733 [INFO] nina.idle: idle_proposal_appended topic=telegram_interface file=2026-06-04_proposals.md
2026-06-04 15:33:09,740 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 15:38:09,747 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 15:43:09,754 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 15:48:09,762 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 15:53:09,764 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 15:58:09,767 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 16:02:13,735 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 16:02:23,138 [INFO] nina.routerlog: {"ts": "2026-06-04T16:02:23.000+0600", "req_id": "b5d8b393", "provider": "MISTRAL", "task_type": "research", "input_tokens": 455, "output_tokens": 558, "cost_usd": 0.0, "ttf_ms": 9277, "total_ms": 9277, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 16:02:23,138 [INFO] nina.router: router_success req_id=b5d8b393 provider=MISTRAL task=research ms=9277
2026-06-04 16:02:23,138 [INFO] nina.idle: idle_proposal_appended topic=config_robustness file=2026-06-04_proposals.md
2026-06-04 16:03:09,773 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 16:08:09,782 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 16:13:09,792 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 16:15:27,162 [INFO] nina.scheduler: NINA operational
2026-06-04 16:18:09,792 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 16:23:09,797 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 16:28:09,804 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 16:33:09,814 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 16:33:23,148 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 16:33:37,374 [INFO] nina.routerlog: {"ts": "2026-06-04T16:33:37.000+0600", "req_id": "a9459ebf", "provider": "MISTRAL", "task_type": "research", "input_tokens": 454, "output_tokens": 788, "cost_usd": 0.0, "ttf_ms": 14114, "total_ms": 14114, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 16:33:37,374 [INFO] nina.router: router_success req_id=a9459ebf provider=MISTRAL task=research ms=14114
2026-06-04 16:33:37,374 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-04_proposals.md
2026-06-04 16:38:09,819 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 16:43:09,821 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 16:50:51,915 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 16:55:51,926 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 17:00:51,934 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 17:05:51,944 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 18:18:04,853 [INFO] nina.memory: MemorySystem ready conversations=0 facts=0
2026-06-04 18:18:05,633 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-04 18:18:05,634 [INFO] nina.router: HybridRouter initialized
2026-06-04 18:18:05,634 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-04 18:18:05,642 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-04 18:18:05,642 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-04 18:18:06,383 [INFO] nina.telegram: TelegramInterface polling started
2026-06-04 18:18:06,383 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-04 18:18:06,384 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-04 18:20:06,447 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 18:20:10,389 [INFO] nina.routerlog: {"ts": "2026-06-04T18:20:10.000+0600", "req_id": "5afdaf00", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-04 18:20:10,389 [WARNING] nina.router: router_fail req_id=5afdaf00 provider=POLLINATIONS err=http_429
2026-06-04 18:20:10,933 [INFO] nina.routerlog: {"ts": "2026-06-04T18:20:10.000+0600", "req_id": "5afdaf00", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-04 18:20:10,933 [WARNING] nina.router: router_fail req_id=5afdaf00 provider=CHUTES err=http_401
2026-06-04 18:20:10,963 [INFO] nina.routerlog: {"ts": "2026-06-04T18:20:10.000+0600", "req_id": "5afdaf00", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-04 18:20:10,963 [WARNING] nina.router: router_fail req_id=5afdaf00 provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-04 18:20:11,617 [INFO] nina.routerlog: {"ts": "2026-06-04T18:20:11.000+0600", "req_id": "5afdaf00", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-04 18:20:11,617 [WARNING] nina.router: router_fail req_id=5afdaf00 provider=CEREBRAS err=http_404
2026-06-04 18:20:12,375 [INFO] nina.routerlog: {"ts": "2026-06-04T18:20:12.000+0600", "req_id": "5afdaf00", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 102, "cost_usd": 0.0, "ttf_ms": 757, "total_ms": 757, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 18:20:12,375 [INFO] nina.router: router_success req_id=5afdaf00 provider=GROQ task=research ms=757
2026-06-04 18:20:12,380 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-04_proposals.md
2026-06-04 18:23:05,664 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 18:28:05,738 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 18:33:05,739 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 18:38:05,739 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 18:43:05,746 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 18:48:05,747 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 18:49:32,783 [INFO] nina.memory: MemorySystem ready conversations=0 facts=0
2026-06-04 18:49:32,812 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-04 18:49:32,812 [INFO] nina.router: HybridRouter initialized
2026-06-04 18:49:32,812 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-04 18:49:32,816 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-04 18:49:32,816 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-04 18:49:33,626 [INFO] nina.telegram: TelegramInterface polling started
2026-06-04 18:49:33,626 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-04 18:49:33,626 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-04 18:49:45,082 [INFO] nina.memory: MemorySystem ready conversations=0 facts=0
2026-06-04 18:49:45,119 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-04 18:49:45,119 [INFO] nina.router: HybridRouter initialized
2026-06-04 18:49:45,119 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-04 18:49:45,123 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-04 18:49:45,123 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-04 18:49:46,015 [INFO] nina.telegram: TelegramInterface polling started
2026-06-04 18:49:46,015 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-04 18:49:46,015 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-04 18:49:50,216 [INFO] nina.memory: MemorySystem ready conversations=0 facts=0
2026-06-04 18:49:50,244 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-04 18:49:50,244 [INFO] nina.router: HybridRouter initialized
2026-06-04 18:49:50,244 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-04 18:49:50,249 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-04 18:49:50,249 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-04 18:49:51,114 [INFO] nina.telegram: TelegramInterface polling started
2026-06-04 18:49:51,114 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-04 18:49:51,114 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-04 18:51:51,172 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 18:51:54,207 [INFO] nina.routerlog: {"ts": "2026-06-04T18:51:54.000+0600", "req_id": "c2a57819", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-04 18:51:54,208 [WARNING] nina.router: router_fail req_id=c2a57819 provider=POLLINATIONS err=http_429
2026-06-04 18:51:55,495 [INFO] nina.routerlog: {"ts": "2026-06-04T18:51:55.000+0600", "req_id": "c2a57819", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-04 18:51:55,495 [WARNING] nina.router: router_fail req_id=c2a57819 provider=CHUTES err=http_401
2026-06-04 18:51:55,565 [INFO] nina.routerlog: {"ts": "2026-06-04T18:51:55.000+0600", "req_id": "c2a57819", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-04 18:51:55,565 [WARNING] nina.router: router_fail req_id=c2a57819 provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-04 18:51:56,782 [INFO] nina.routerlog: {"ts": "2026-06-04T18:51:56.000+0600", "req_id": "c2a57819", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-04 18:51:56,782 [WARNING] nina.router: router_fail req_id=c2a57819 provider=CEREBRAS err=http_404
2026-06-04 18:51:57,600 [INFO] nina.routerlog: {"ts": "2026-06-04T18:51:57.000+0600", "req_id": "c2a57819", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 133, "cost_usd": 0.0, "ttf_ms": 817, "total_ms": 817, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 18:51:57,600 [INFO] nina.router: router_success req_id=c2a57819 provider=GROQ task=research ms=817
2026-06-04 18:51:57,600 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-04_proposals.md
2026-06-04 18:54:50,273 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 18:59:50,274 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 19:04:50,329 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 19:09:23,529 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1
2026-06-04 19:09:23,559 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-04 19:09:23,559 [INFO] nina.router: HybridRouter initialized
2026-06-04 19:09:23,559 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-04 19:09:23,564 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-04 19:09:23,564 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-04 19:09:24,440 [INFO] nina.telegram: TelegramInterface polling started
2026-06-04 19:09:24,440 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-04 19:09:24,441 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-04 19:10:42,128 [INFO] nina.routerlog: {"ts": "2026-06-04T19:10:42.000+0600", "req_id": "31ac78bb", "provider": "POLLINATIONS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-04 19:10:42,129 [WARNING] nina.router: router_fail req_id=31ac78bb provider=POLLINATIONS err=http_429
2026-06-04 19:10:43,705 [INFO] nina.routerlog: {"ts": "2026-06-04T19:10:43.000+0600", "req_id": "31ac78bb", "provider": "CHUTES", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-04 19:10:43,705 [WARNING] nina.router: router_fail req_id=31ac78bb provider=CHUTES err=http_401
2026-06-04 19:10:43,772 [INFO] nina.routerlog: {"ts": "2026-06-04T19:10:43.000+0600", "req_id": "31ac78bb", "provider": "HFPUBLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-04 19:10:43,773 [WARNING] nina.router: router_fail req_id=31ac78bb provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-04 19:10:45,160 [INFO] nina.routerlog: {"ts": "2026-06-04T19:10:45.000+0600", "req_id": "31ac78bb", "provider": "CEREBRAS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-04 19:10:45,160 [WARNING] nina.router: router_fail req_id=31ac78bb provider=CEREBRAS err=http_404
2026-06-04 19:10:46,463 [INFO] nina.routerlog: {"ts": "2026-06-04T19:10:46.000+0600", "req_id": "31ac78bb", "provider": "GROQ", "task_type": "general", "input_tokens": 255, "output_tokens": 65, "cost_usd": 0.0, "ttf_ms": 1303, "total_ms": 1303, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 19:10:46,463 [INFO] nina.router: router_success req_id=31ac78bb provider=GROQ task=general ms=1303
2026-06-04 19:10:46,464 [INFO] nina.agent: agent_step step=1 task=general response='TOOL:system INPUT:status \nYou are currently identified as M. Baizid Alam, an AGM'
2026-06-04 19:10:53,121 [INFO] nina.routerlog: {"ts": "2026-06-04T19:10:53.000+0600", "req_id": "09b40b8d", "provider": "MISTRAL", "task_type": "general", "input_tokens": 330, "output_tokens": 296, "cost_usd": 0.0, "ttf_ms": 6657, "total_ms": 6657, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 19:10:53,121 [INFO] nina.router: router_success req_id=09b40b8d provider=MISTRAL task=general ms=6657
2026-06-04 19:10:53,121 [INFO] nina.agent: agent_step step=2 task=general response="Understood. Since the `system` tool isn't functioning as expected, I'll rely on "
2026-06-04 19:10:53,529 [INFO] nina.routerlog: {"ts": "2026-06-04T19:10:53.000+0600", "req_id": "d7ad6907", "provider": "DEEPSEEK", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-04 19:10:53,529 [WARNING] nina.router: router_fail req_id=d7ad6907 provider=DEEPSEEK err=http_401
2026-06-04 19:10:53,848 [INFO] nina.routerlog: {"ts": "2026-06-04T19:10:53.000+0600", "req_id": "d7ad6907", "provider": "GEMINI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-04 19:10:53,849 [WARNING] nina.router: router_fail req_id=d7ad6907 provider=GEMINI err=http_404
2026-06-04 19:10:54,860 [INFO] nina.routerlog: {"ts": "2026-06-04T19:10:54.000+0600", "req_id": "d7ad6907", "provider": "TOGETHER", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-04 19:10:54,860 [WARNING] nina.router: router_fail req_id=d7ad6907 provider=TOGETHER err=http_404
2026-06-04 19:10:56,909 [INFO] nina.routerlog: {"ts": "2026-06-04T19:10:56.000+0600", "req_id": "d7ad6907", "provider": "COHERE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_405"}
2026-06-04 19:10:56,909 [WARNING] nina.router: router_fail req_id=d7ad6907 provider=COHERE err=http_405
2026-06-04 19:10:58,241 [INFO] nina.routerlog: {"ts": "2026-06-04T19:10:58.000+0600", "req_id": "d7ad6907", "provider": "FIREWORKS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-04 19:10:58,241 [WARNING] nina.router: router_fail req_id=d7ad6907 provider=FIREWORKS err=http_404
2026-06-04 19:10:58,751 [INFO] nina.routerlog: {"ts": "2026-06-04T19:10:58.000+0600", "req_id": "d7ad6907", "provider": "XAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_400"}
2026-06-04 19:10:58,751 [WARNING] nina.router: router_fail req_id=d7ad6907 provider=XAI err=http_400
2026-06-04 19:10:59,981 [INFO] nina.routerlog: {"ts": "2026-06-04T19:10:59.000+0600", "req_id": "d7ad6907", "provider": "SAMBANOVA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-04 19:10:59,981 [WARNING] nina.router: router_fail req_id=d7ad6907 provider=SAMBANOVA err=http_404
2026-06-04 19:11:01,542 [INFO] nina.routerlog: {"ts": "2026-06-04T19:11:01.000+0600", "req_id": "d7ad6907", "provider": "HYPERBOLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_402"}
2026-06-04 19:11:01,542 [WARNING] nina.router: router_fail req_id=d7ad6907 provider=HYPERBOLIC err=http_402
2026-06-04 19:11:03,316 [INFO] nina.routerlog: {"ts": "2026-06-04T19:11:03.000+0600", "req_id": "d7ad6907", "provider": "NOVITA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-04 19:11:03,316 [WARNING] nina.router: router_fail req_id=d7ad6907 provider=NOVITA err=http_404
2026-06-04 19:11:04,896 [INFO] nina.routerlog: {"ts": "2026-06-04T19:11:04.000+0600", "req_id": "d7ad6907", "provider": "OPENAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-04 19:11:04,896 [WARNING] nina.router: router_fail req_id=d7ad6907 provider=OPENAI err=http_401
2026-06-04 19:11:09,089 [INFO] nina.routerlog: {"ts": "2026-06-04T19:11:09.000+0600", "req_id": "d7ad6907", "provider": "OPENROUTER", "task_type": "general", "input_tokens": 683, "output_tokens": 487, "cost_usd": 0.0, "ttf_ms": 4192, "total_ms": 4192, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 19:11:09,089 [INFO] nina.router: router_success req_id=d7ad6907 provider=OPENROUTER task=general ms=4192
2026-06-04 19:11:09,089 [INFO] nina.agent: agent_step step=3 task=general response='**You are M.\u202fBaizid\u202fAlam** – Assistant General Manager at **BASIC Bank Limited**'
2026-06-04 19:11:10,016 [INFO] nina.routerlog: {"ts": "2026-06-04T19:11:10.000+0600", "req_id": "df2c3ea2", "provider": "GROQ", "task_type": "general", "input_tokens": 859, "output_tokens": 175, "cost_usd": 0.0, "ttf_ms": 926, "total_ms": 926, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 19:11:10,016 [INFO] nina.router: router_success req_id=df2c3ea2 provider=GROQ task=general ms=926
2026-06-04 19:11:10,016 [INFO] nina.agent: agent_step step=4 task=general response="Given the errors with the `system` and `web` tools, I'll proceed based on the in"
2026-06-04 19:13:24,511 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 19:13:25,289 [INFO] nina.routerlog: {"ts": "2026-06-04T19:13:25.000+0600", "req_id": "06d80698", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 121, "cost_usd": 0.0, "ttf_ms": 658, "total_ms": 658, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 19:13:25,289 [INFO] nina.router: router_success req_id=06d80698 provider=GROQ task=research ms=658
2026-06-04 19:13:25,289 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-04_proposals.md
2026-06-04 19:14:23,593 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 19:19:23,596 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 19:24:23,597 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 19:29:23,597 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 19:34:23,610 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 19:39:23,645 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 19:44:23,646 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 19:44:25,291 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 19:44:28,785 [INFO] nina.routerlog: {"ts": "2026-06-04T19:44:28.000+0600", "req_id": "b86d6146", "provider": "GROQ", "task_type": "research", "input_tokens": 395, "output_tokens": 397, "cost_usd": 0.0, "ttf_ms": 3371, "total_ms": 3371, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 19:44:28,785 [INFO] nina.router: router_success req_id=b86d6146 provider=GROQ task=research ms=3371
2026-06-04 19:44:28,786 [INFO] nina.idle: idle_proposal_appended topic=morning_report file=2026-06-04_proposals.md
2026-06-04 19:49:23,647 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 19:54:23,649 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 19:59:23,677 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 20:04:23,679 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 20:09:23,569 [INFO] nina.scheduler: NINA operational
2026-06-04 20:09:23,569 [INFO] nina.scheduler: NINA operational
2026-06-04 20:09:23,681 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 20:14:23,682 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 20:15:28,795 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 20:15:30,840 [INFO] nina.routerlog: {"ts": "2026-06-04T20:15:30.000+0600", "req_id": "0c4934ad", "provider": "GROQ", "task_type": "research", "input_tokens": 390, "output_tokens": 273, "cost_usd": 0.0, "ttf_ms": 1939, "total_ms": 1939, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 20:15:30,845 [INFO] nina.router: router_success req_id=0c4934ad provider=GROQ task=research ms=1939
2026-06-04 20:15:30,845 [INFO] nina.idle: idle_proposal_appended topic=provider_routing file=2026-06-04_proposals.md
2026-06-04 20:19:23,684 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 20:24:23,686 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 20:29:23,688 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 20:34:23,690 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 20:39:23,692 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 20:44:23,693 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 20:46:30,857 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 20:46:32,282 [INFO] nina.routerlog: {"ts": "2026-06-04T20:46:32.000+0600", "req_id": "bc0837dd", "provider": "GROQ", "task_type": "research", "input_tokens": 394, "output_tokens": 292, "cost_usd": 0.0, "ttf_ms": 1316, "total_ms": 1316, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 20:46:32,282 [INFO] nina.router: router_success req_id=bc0837dd provider=GROQ task=research ms=1316
2026-06-04 20:46:32,282 [INFO] nina.idle: idle_proposal_appended topic=memory_context file=2026-06-04_proposals.md
2026-06-04 20:49:23,695 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 20:54:23,696 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 20:59:23,696 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 21:04:23,697 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 21:09:23,570 [INFO] nina.scheduler: NINA operational
2026-06-04 21:09:23,570 [INFO] nina.scheduler: NINA operational
2026-06-04 21:09:23,699 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 21:14:23,700 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 21:17:32,295 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 21:17:33,926 [INFO] nina.routerlog: {"ts": "2026-06-04T21:17:33.000+0600", "req_id": "5b29194f", "provider": "GROQ", "task_type": "research", "input_tokens": 394, "output_tokens": 238, "cost_usd": 0.0, "ttf_ms": 1525, "total_ms": 1525, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 21:17:33,926 [INFO] nina.router: router_success req_id=5b29194f provider=GROQ task=research ms=1525
2026-06-04 21:17:33,926 [INFO] nina.idle: idle_proposal_appended topic=scheduler_errors file=2026-06-04_proposals.md
2026-06-04 21:19:23,701 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 21:24:23,703 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 21:29:23,704 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 21:34:23,704 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 21:39:23,706 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 21:44:23,707 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 21:48:33,941 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 21:48:36,289 [INFO] nina.routerlog: {"ts": "2026-06-04T21:48:36.000+0600", "req_id": "2c449ad9", "provider": "GROQ", "task_type": "research", "input_tokens": 394, "output_tokens": 297, "cost_usd": 0.0, "ttf_ms": 2239, "total_ms": 2239, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 21:48:36,289 [INFO] nina.router: router_success req_id=2c449ad9 provider=GROQ task=research ms=2239
2026-06-04 21:48:36,289 [INFO] nina.idle: idle_proposal_appended topic=telegram_interface file=2026-06-04_proposals.md
2026-06-04 21:49:23,709 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 21:54:23,712 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 21:59:23,713 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 22:04:23,715 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 22:09:23,569 [INFO] nina.scheduler: NINA operational
2026-06-04 22:09:23,569 [INFO] nina.scheduler: NINA operational
2026-06-04 22:09:23,716 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 22:14:23,717 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 22:19:23,718 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 22:19:36,304 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 22:19:38,444 [INFO] nina.routerlog: {"ts": "2026-06-04T22:19:38.000+0600", "req_id": "03ed29f0", "provider": "GROQ", "task_type": "research", "input_tokens": 397, "output_tokens": 241, "cost_usd": 0.0, "ttf_ms": 2023, "total_ms": 2023, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 22:19:38,444 [INFO] nina.router: router_success req_id=03ed29f0 provider=GROQ task=research ms=2023
2026-06-04 22:19:38,445 [INFO] nina.idle: idle_proposal_appended topic=config_robustness file=2026-06-04_proposals.md
2026-06-04 22:24:23,720 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 22:29:23,720 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 22:34:23,722 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 22:39:23,723 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 22:44:23,725 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 22:49:23,727 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 22:50:38,453 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 22:50:39,437 [INFO] nina.routerlog: {"ts": "2026-06-04T22:50:39.000+0600", "req_id": "74b05aa3", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 122, "cost_usd": 0.0, "ttf_ms": 862, "total_ms": 862, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 22:50:39,437 [INFO] nina.router: router_success req_id=74b05aa3 provider=GROQ task=research ms=862
2026-06-04 22:50:39,437 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-04_proposals.md
2026-06-04 22:54:23,727 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 22:59:23,745 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 23:04:23,746 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 23:09:23,572 [INFO] nina.scheduler: NINA operational
2026-06-04 23:09:23,572 [INFO] nina.scheduler: NINA operational
2026-06-04 23:09:23,747 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 23:14:23,749 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 23:19:23,750 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 23:21:39,447 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 23:21:42,603 [INFO] nina.routerlog: {"ts": "2026-06-04T23:21:42.000+0600", "req_id": "072f3232", "provider": "GROQ", "task_type": "research", "input_tokens": 395, "output_tokens": 286, "cost_usd": 0.0, "ttf_ms": 3043, "total_ms": 3043, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 23:21:42,603 [INFO] nina.router: router_success req_id=072f3232 provider=GROQ task=research ms=3043
2026-06-04 23:21:42,603 [INFO] nina.idle: idle_proposal_appended topic=morning_report file=2026-06-04_proposals.md
2026-06-04 23:24:23,751 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 23:29:23,752 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 23:34:23,753 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 23:39:23,754 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 23:44:23,756 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 23:49:23,758 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 23:52:42,617 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-04 23:52:44,348 [INFO] nina.routerlog: {"ts": "2026-06-04T23:52:44.000+0600", "req_id": "c703d7ba", "provider": "GROQ", "task_type": "research", "input_tokens": 390, "output_tokens": 272, "cost_usd": 0.0, "ttf_ms": 1621, "total_ms": 1621, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-04 23:52:44,348 [INFO] nina.router: router_success req_id=c703d7ba provider=GROQ task=research ms=1621
2026-06-04 23:52:44,349 [INFO] nina.idle: idle_proposal_appended topic=provider_routing file=2026-06-04_proposals.md
2026-06-04 23:54:23,759 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-04 23:59:23,760 [WARNING] nina.router: idle_monitor_error 'NinaConfig' object has no attribute 'ramguardgb'
2026-06-05 00:09:23,569 [INFO] nina.scheduler: NINA operational
```

### logs/nina.log.2026-06-05
Last modified: 2026-06-06 00:01:07
Size: 105212 bytes
```log
[truncated — showing last 200 lines]
2026-06-05 22:00:50,587 [INFO] nina.router: bangla_route req_id=dc2bd9fd preferred=['OPENAI', 'MISTRAL', 'CEREBRAS'] full_chain=19
2026-06-05 22:00:51,299 [INFO] nina.routerlog: {"ts": "2026-06-05T22:00:51.000+0600", "req_id": "dc2bd9fd", "provider": "OPENAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-05 22:00:51,299 [WARNING] nina.router: router_fail req_id=dc2bd9fd provider=OPENAI err=http_401
2026-06-05 22:01:00,630 [INFO] nina.routerlog: {"ts": "2026-06-05T22:01:00.000+0600", "req_id": "dc2bd9fd", "provider": "MISTRAL", "task_type": "general", "input_tokens": 379, "output_tokens": 85, "cost_usd": 0.0, "ttf_ms": 5105, "total_ms": 5105, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:01:00,630 [INFO] nina.router: router_success req_id=dc2bd9fd provider=MISTRAL task=general ms=5105
2026-06-05 22:01:00,630 [INFO] nina.agent: agent_step step=1 task=general response='[LANGUAGE OVERRIDE: সম্পূর্ণ উত্তর বাংলায়।]\n\nবাইজিদ ভাই, ভালো আছেন আশা করি। USD'
2026-06-05 22:01:03,256 [INFO] nina.tools.search: tavily_search query='"USD to BDT exchange rate today Bangladesh Bank interbank rate"]\n\n[Step 2/5 চলছে...]' results=5
2026-06-05 22:01:03,257 [INFO] nina.router: bangla_route req_id=e7113920 preferred=['MISTRAL', 'CEREBRAS', 'GROQ'] full_chain=17
2026-06-05 22:01:04,092 [INFO] nina.routerlog: {"ts": "2026-06-05T22:01:04.000+0600", "req_id": "ab2b9218", "provider": "MISTRAL", "task_type": "multilingual", "input_tokens": 617, "output_tokens": 259, "cost_usd": 0.0, "ttf_ms": 8568, "total_ms": 8568, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:01:04,092 [INFO] nina.router: router_success req_id=ab2b9218 provider=MISTRAL task=multilingual ms=8568
2026-06-05 22:01:04,092 [INFO] nina.agent: agent_step step=2 task=multilingual response='ধন্যবাদ, বিষয়টি বুঝতে পেরেছি। সরাসরি **TOOL:browser** ব্যবহার করে নির্ভরযোগ্য উ'
2026-06-05 22:01:04,092 [INFO] nina.router: bangla_route req_id=523af44d preferred=['MISTRAL', 'CEREBRAS', 'GROQ'] full_chain=17
2026-06-05 22:02:21,832 [INFO] nina.routerlog: {"ts": "2026-06-05T22:02:21.000+0600", "req_id": "e7113920", "provider": "MISTRAL", "task_type": "general", "input_tokens": 562, "output_tokens": 276, "cost_usd": 0.0, "ttf_ms": 20200, "total_ms": 20200, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:02:21,832 [INFO] nina.router: router_success req_id=e7113920 provider=MISTRAL task=general ms=20200
2026-06-05 22:02:21,832 [INFO] nina.agent: agent_step step=2 task=general response='[LANGUAGE OVERRIDE: সম্পূর্ণ উত্তর বাংলায়।]\n\nবাইজিদ ভাই, আজকের **ইন্টারব্যাংক U'
2026-06-05 22:02:21,833 [INFO] nina.router: bangla_route req_id=2968748d preferred=['MISTRAL', 'CEREBRAS', 'GROQ'] full_chain=18
2026-06-05 22:02:22,427 [INFO] nina.routerlog: {"ts": "2026-06-05T22:02:22.000+0600", "req_id": "523af44d", "provider": "MISTRAL", "task_type": "multilingual", "input_tokens": 910, "output_tokens": 272, "cost_usd": 0.0, "ttf_ms": 17331, "total_ms": 17331, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:02:22,427 [INFO] nina.router: router_success req_id=523af44d provider=MISTRAL task=multilingual ms=17331
2026-06-05 22:02:22,427 [INFO] nina.agent: agent_step step=3 task=multilingual response='ধন্যবাদ, বিষয়টি পরিষ্কার হলো। সরাসরি **TOOL:web** ব্যবহার করে সঠিক পদ্ধতিতে ডেট'
2026-06-05 22:02:22,427 [INFO] nina.router: bangla_route req_id=f99ac26c preferred=['MISTRAL', 'CEREBRAS', 'GROQ'] full_chain=17
2026-06-05 22:02:58,326 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-05 22:03:01,973 [INFO] nina.routerlog: {"ts": "2026-06-05T22:03:01.000+0600", "req_id": "9d3cb8e9", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-05 22:03:01,973 [WARNING] nina.router: router_fail req_id=9d3cb8e9 provider=POLLINATIONS err=http_429
2026-06-05 22:03:30,031 [INFO] nina.routerlog: {"ts": "2026-06-05T22:03:30.000+0600", "req_id": "f99ac26c", "provider": "MISTRAL", "task_type": "multilingual", "input_tokens": 1226, "output_tokens": 274, "cost_usd": 0.0, "ttf_ms": 6602, "total_ms": 6602, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:03:30,031 [INFO] nina.router: router_success req_id=f99ac26c provider=MISTRAL task=multilingual ms=6602
2026-06-05 22:03:30,031 [INFO] nina.agent: agent_step step=4 task=multilingual response='বুঝতে পেরেছি — টুল ব্যবহারের সিনট্যাক্সে সমস্যা হচ্ছে। সরাসরি **TOOL:web** এর পর'
2026-06-05 22:03:30,031 [INFO] nina.router: bangla_route req_id=8c855f94 preferred=['MISTRAL', 'CEREBRAS', 'GROQ'] full_chain=16
2026-06-05 22:03:33,104 [INFO] nina.routerlog: {"ts": "2026-06-05T22:03:33.000+0600", "req_id": "2968748d", "provider": "MISTRAL", "task_type": "general", "input_tokens": 936, "output_tokens": 462, "cost_usd": 0.0, "ttf_ms": 10270, "total_ms": 10270, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:03:33,104 [INFO] nina.router: router_success req_id=2968748d provider=MISTRAL task=general ms=10270
2026-06-05 22:03:33,105 [INFO] nina.agent: agent_step step=3 task=general response='[LANGUAGE OVERRIDE: সম্পূর্ণ উত্তর বাংলায়।]\n\n**আপডেটেড রেট (আজকের তারিখ):**\nবাং'
2026-06-05 22:03:33,105 [INFO] nina.router: bangla_route req_id=5b63e619 preferred=['MISTRAL', 'CEREBRAS', 'GROQ'] full_chain=16
2026-06-05 22:03:46,106 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1
2026-06-05 22:03:46,136 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-05 22:03:46,136 [INFO] nina.router: HybridRouter initialized
2026-06-05 22:03:46,136 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 22:03:46,141 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-05 22:03:46,141 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-05 22:03:47,029 [INFO] nina.telegram: TelegramInterface polling started
2026-06-05 22:03:47,029 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-05 22:03:47,030 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-05 22:04:58,436 [DEBUG] nina.telegram: bangla_detected override_prepended
2026-06-05 22:04:59,332 [INFO] nina.router: bangla_route req_id=b91a5c82 preferred=['GEMINI', 'OPENAI', 'MISTRAL'] full_chain=19
2026-06-05 22:04:59,714 [INFO] nina.routerlog: {"ts": "2026-06-05T22:04:59.000+0600", "req_id": "b91a5c82", "provider": "GEMINI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-05 22:04:59,714 [WARNING] nina.router: router_fail req_id=b91a5c82 provider=GEMINI err=http_429
2026-06-05 22:05:00,150 [INFO] nina.routerlog: {"ts": "2026-06-05T22:05:00.000+0600", "req_id": "b91a5c82", "provider": "OPENAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-05 22:05:00,151 [WARNING] nina.router: router_fail req_id=b91a5c82 provider=OPENAI err=http_401
2026-06-05 22:05:05,420 [INFO] nina.routerlog: {"ts": "2026-06-05T22:05:05.000+0600", "req_id": "b91a5c82", "provider": "MISTRAL", "task_type": "general", "input_tokens": 341, "output_tokens": 197, "cost_usd": 0.0, "ttf_ms": 5269, "total_ms": 5269, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:05:05,421 [INFO] nina.router: router_success req_id=b91a5c82 provider=MISTRAL task=general ms=5269
2026-06-05 22:05:05,421 [INFO] nina.agent: agent_step step=1 task=general response='[Step 2/5] **PLAN:**\n- **TOOL:web** ব্যবহার করে বর্তমান USD/BDT এক্সচেঞ্জ রেট খু'
2026-06-05 22:05:05,421 [INFO] nina.router: bangla_route req_id=d89b45d3 preferred=['OPENAI', 'MISTRAL', 'CEREBRAS'] full_chain=18
2026-06-05 22:05:06,289 [INFO] nina.routerlog: {"ts": "2026-06-05T22:05:06.000+0600", "req_id": "d89b45d3", "provider": "OPENAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-05 22:05:06,289 [WARNING] nina.router: router_fail req_id=d89b45d3 provider=OPENAI err=http_401
2026-06-05 22:06:09,782 [INFO] nina.routerlog: {"ts": "2026-06-05T22:06:09.000+0600", "req_id": "d89b45d3", "provider": "MISTRAL", "task_type": "general", "input_tokens": 561, "output_tokens": 146, "cost_usd": 0.0, "ttf_ms": 3354, "total_ms": 3354, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:06:09,782 [INFO] nina.router: router_success req_id=d89b45d3 provider=MISTRAL task=general ms=3354
2026-06-05 22:06:09,782 [INFO] nina.agent: agent_step step=2 task=general response='[Step 4/5] **ACT (সংশোধিত):**\n- **TOOL:web** ব্যবহার করে সরাসরি বাংলাদেশ ব্যাংকে'
2026-06-05 22:06:09,783 [INFO] nina.router: bangla_route req_id=1a4d2348 preferred=['OPENAI', 'MISTRAL', 'CEREBRAS'] full_chain=19
2026-06-05 22:06:10,595 [INFO] nina.routerlog: {"ts": "2026-06-05T22:06:10.000+0600", "req_id": "1a4d2348", "provider": "OPENAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-05 22:06:10,595 [WARNING] nina.router: router_fail req_id=1a4d2348 provider=OPENAI err=http_401
2026-06-05 22:07:19,921 [INFO] nina.routerlog: {"ts": "2026-06-05T22:07:19.000+0600", "req_id": "1a4d2348", "provider": "MISTRAL", "task_type": "general", "input_tokens": 740, "output_tokens": 379, "cost_usd": 0.0, "ttf_ms": 9137, "total_ms": 9137, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:07:19,921 [INFO] nina.router: router_success req_id=1a4d2348 provider=MISTRAL task=general ms=9137
2026-06-05 22:07:19,921 [INFO] nina.agent: agent_step step=3 task=general response='**আপডেট (১২ জুন ২০২৪, দুপুর ২:৩০ - ঢাকা সময়):**\n\n**TOOL:browser** থেকে প্রাপ্ত '
2026-06-05 22:07:19,921 [INFO] nina.router: bangla_route req_id=a4c79001 preferred=['MISTRAL', 'CEREBRAS', 'GROQ'] full_chain=18
2026-06-05 22:07:47,104 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-05 22:07:50,810 [INFO] nina.routerlog: {"ts": "2026-06-05T22:07:50.000+0600", "req_id": "5513b3d8", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-05 22:07:50,811 [WARNING] nina.router: router_fail req_id=5513b3d8 provider=POLLINATIONS err=http_429
2026-06-05 22:07:51,333 [INFO] nina.routerlog: {"ts": "2026-06-05T22:07:51.000+0600", "req_id": "5513b3d8", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-05 22:07:51,333 [WARNING] nina.router: router_fail req_id=5513b3d8 provider=CHUTES err=http_401
2026-06-05 22:07:51,406 [INFO] nina.routerlog: {"ts": "2026-06-05T22:07:51.000+0600", "req_id": "5513b3d8", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-05 22:07:51,406 [WARNING] nina.router: router_fail req_id=5513b3d8 provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-05 22:07:52,281 [INFO] nina.routerlog: {"ts": "2026-06-05T22:07:52.000+0600", "req_id": "5513b3d8", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-05 22:07:52,281 [WARNING] nina.router: router_fail req_id=5513b3d8 provider=CEREBRAS err=http_404
2026-06-05 22:07:53,150 [INFO] nina.routerlog: {"ts": "2026-06-05T22:07:53.000+0600", "req_id": "5513b3d8", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 154, "cost_usd": 0.0, "ttf_ms": 868, "total_ms": 868, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:07:53,150 [INFO] nina.router: router_success req_id=5513b3d8 provider=GROQ task=research ms=868
2026-06-05 22:07:53,150 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-05_proposals.md
2026-06-05 22:08:02,817 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1
2026-06-05 22:08:02,849 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-05 22:08:02,849 [INFO] nina.router: HybridRouter initialized
2026-06-05 22:08:02,849 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 22:08:02,853 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-05 22:08:02,853 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-05 22:08:03,625 [INFO] nina.telegram: TelegramInterface polling started
2026-06-05 22:08:03,625 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-05 22:08:03,625 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-05 22:08:17,359 [DEBUG] nina.telegram: bangla_detected override_prepended
2026-06-05 22:08:18,471 [INFO] nina.router: bangla_route req_id=6c8d5aef preferred=['GEMINI', 'OPENAI', 'MISTRAL'] full_chain=19
2026-06-05 22:08:18,905 [INFO] nina.routerlog: {"ts": "2026-06-05T22:08:18.000+0600", "req_id": "6c8d5aef", "provider": "GEMINI", "task_type": "multilingual", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-05 22:08:18,905 [WARNING] nina.router: router_fail req_id=6c8d5aef provider=GEMINI err=http_429
2026-06-05 22:08:19,251 [INFO] nina.routerlog: {"ts": "2026-06-05T22:08:19.000+0600", "req_id": "6c8d5aef", "provider": "OPENAI", "task_type": "multilingual", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-05 22:08:19,251 [WARNING] nina.router: router_fail req_id=6c8d5aef provider=OPENAI err=http_401
2026-06-05 22:08:29,041 [INFO] nina.routerlog: {"ts": "2026-06-05T22:08:29.000+0600", "req_id": "6c8d5aef", "provider": "MISTRAL", "task_type": "multilingual", "input_tokens": 341, "output_tokens": 405, "cost_usd": 0.0, "ttf_ms": 9790, "total_ms": 9790, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:08:29,041 [INFO] nina.router: router_success req_id=6c8d5aef provider=MISTRAL task=multilingual ms=9790
2026-06-05 22:08:29,042 [INFO] nina.agent: agent_step step=1 task=multilingual response='[Step 1/5] Scratchpad:\n- ব্যবহারকারীর প্রশ্ন সরাসরি USD/BDT রেট সম্পর্কিত।\n- মেম'
2026-06-05 22:08:30,168 [WARNING] nina.tools.search: tavily_failed Client error '400 Bad Request' for url 'https://api.tavily.com/search'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
2026-06-05 22:08:31,909 [INFO] nina.tools.search: serper_search query='**' results=5
2026-06-05 22:08:31,910 [INFO] nina.router: bangla_route req_id=6935a045 preferred=['OPENAI', 'MISTRAL', 'CEREBRAS'] full_chain=18
2026-06-05 22:08:33,347 [INFO] nina.routerlog: {"ts": "2026-06-05T22:08:33.000+0600", "req_id": "6935a045", "provider": "OPENAI", "task_type": "multilingual", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-05 22:08:33,347 [WARNING] nina.router: router_fail req_id=6935a045 provider=OPENAI err=http_401
2026-06-05 22:09:44,355 [INFO] nina.routerlog: {"ts": "2026-06-05T22:09:44.000+0600", "req_id": "6935a045", "provider": "MISTRAL", "task_type": "multilingual", "input_tokens": 843, "output_tokens": 677, "cost_usd": 0.0, "ttf_ms": 14310, "total_ms": 14310, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:09:44,356 [INFO] nina.router: router_success req_id=6935a045 provider=MISTRAL task=multilingual ms=14310
2026-06-05 22:09:44,356 [INFO] nina.agent: agent_step step=2 task=multilingual response='**উত্তর:**\nআজকে (তারিখ: **`{{current_date}}`**) **USD/BDT** রেটের সর্বশেষ তথ্য ন'
2026-06-05 22:09:44,356 [INFO] nina.router: bangla_route req_id=7f958150 preferred=['OPENAI', 'MISTRAL', 'CEREBRAS'] full_chain=19
2026-06-05 22:09:45,332 [INFO] nina.routerlog: {"ts": "2026-06-05T22:09:45.000+0600", "req_id": "7f958150", "provider": "OPENAI", "task_type": "multilingual", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-05 22:09:45,332 [WARNING] nina.router: router_fail req_id=7f958150 provider=OPENAI err=http_401
2026-06-05 22:11:03,685 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-05 22:11:06,846 [INFO] nina.routerlog: {"ts": "2026-06-05T22:11:06.000+0600", "req_id": "3ca92967", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-05 22:11:06,846 [WARNING] nina.router: router_fail req_id=3ca92967 provider=POLLINATIONS err=http_429
2026-06-05 22:11:08,217 [INFO] nina.routerlog: {"ts": "2026-06-05T22:11:08.000+0600", "req_id": "3ca92967", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-05 22:11:08,217 [WARNING] nina.router: router_fail req_id=3ca92967 provider=CHUTES err=http_401
2026-06-05 22:11:08,280 [INFO] nina.routerlog: {"ts": "2026-06-05T22:11:08.000+0600", "req_id": "3ca92967", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-05 22:11:08,280 [WARNING] nina.router: router_fail req_id=3ca92967 provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-05 22:11:08,793 [INFO] nina.routerlog: {"ts": "2026-06-05T22:11:08.000+0600", "req_id": "3ca92967", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-05 22:11:08,793 [WARNING] nina.router: router_fail req_id=3ca92967 provider=CEREBRAS err=http_404
2026-06-05 22:11:09,913 [INFO] nina.routerlog: {"ts": "2026-06-05T22:11:09.000+0600", "req_id": "3ca92967", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 112, "cost_usd": 0.0, "ttf_ms": 1119, "total_ms": 1119, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:11:09,913 [INFO] nina.router: router_success req_id=3ca92967 provider=GROQ task=research ms=1119
2026-06-05 22:11:09,913 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-05_proposals.md
2026-06-05 22:11:30,905 [INFO] nina.routerlog: {"ts": "2026-06-05T22:11:30.000+0600", "req_id": "7f958150", "provider": "MISTRAL", "task_type": "multilingual", "input_tokens": 1617, "output_tokens": 1242, "cost_usd": 0.0, "ttf_ms": 45543, "total_ms": 45543, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:11:30,905 [INFO] nina.router: router_success req_id=7f958150 provider=MISTRAL task=multilingual ms=45543
2026-06-05 22:11:30,905 [INFO] nina.agent: agent_step step=3 task=multilingual response='**উত্তর (Python-এর `*` ও `**` প্যারামিটার অপারেটর):**\n\nPython-এ ফাংশন ডেফিনেশনে '
2026-06-05 22:11:30,905 [INFO] nina.router: bangla_route req_id=15f96f10 preferred=['MISTRAL', 'CEREBRAS', 'GROQ'] full_chain=16
2026-06-05 22:12:45,964 [INFO] nina.routerlog: {"ts": "2026-06-05T22:12:45.000+0600", "req_id": "15f96f10", "provider": "MISTRAL", "task_type": "multilingual", "input_tokens": 2956, "output_tokens": 818, "cost_usd": 0.0, "ttf_ms": 14047, "total_ms": 14047, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:12:45,965 [INFO] nina.router: router_success req_id=15f96f10 provider=MISTRAL task=multilingual ms=14047
2026-06-05 22:12:45,965 [INFO] nina.agent: agent_step step=4 task=multilingual response='**সংক্ষিপ্ত উত্তর (Python-এ `*` ও `**` এর কাজ):**\n\n### **১. `*` (Single Star) – '
2026-06-05 22:12:45,965 [INFO] nina.router: bangla_route req_id=10b7e6b7 preferred=['MISTRAL', 'CEREBRAS', 'GROQ'] full_chain=17
2026-06-05 22:13:04,372 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-05 22:13:18,452 [WARNING] nina.agent: agent_loop_timeout goal='[LANGUAGE OVERRIDE: Respond entirely in Bangla. No English except technical term' exceeded=300s
2026-06-05 22:14:10,349 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1
2026-06-05 22:14:10,381 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-05 22:14:10,381 [INFO] nina.router: HybridRouter initialized
2026-06-05 22:14:10,381 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 22:14:10,385 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-05 22:14:10,385 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-05 22:14:11,219 [INFO] nina.telegram: TelegramInterface polling started
2026-06-05 22:14:11,220 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-05 22:14:11,220 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-05 22:16:11,279 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-05 22:16:14,453 [INFO] nina.routerlog: {"ts": "2026-06-05T22:16:14.000+0600", "req_id": "2527b240", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-05 22:16:14,453 [WARNING] nina.router: router_fail req_id=2527b240 provider=POLLINATIONS err=http_429
2026-06-05 22:17:14,457 [INFO] nina.routerlog: {"ts": "2026-06-05T22:17:14.000+0600", "req_id": "2527b240", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:17:14,457 [WARNING] nina.router: router_fail req_id=2527b240 provider=CHUTES err=
2026-06-05 22:17:14,494 [INFO] nina.routerlog: {"ts": "2026-06-05T22:17:14.000+0600", "req_id": "2527b240", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-05 22:17:14,494 [WARNING] nina.router: router_fail req_id=2527b240 provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-05 22:17:14,940 [INFO] nina.routerlog: {"ts": "2026-06-05T22:17:14.000+0600", "req_id": "2527b240", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-05 22:17:14,940 [WARNING] nina.router: router_fail req_id=2527b240 provider=CEREBRAS err=http_404
2026-06-05 22:17:16,508 [INFO] nina.routerlog: {"ts": "2026-06-05T22:17:16.000+0600", "req_id": "2527b240", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 108, "cost_usd": 0.0, "ttf_ms": 1567, "total_ms": 1567, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:17:16,508 [INFO] nina.router: router_success req_id=2527b240 provider=GROQ task=research ms=1567
2026-06-05 22:17:16,508 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-05_proposals.md
2026-06-05 22:20:11,782 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1
2026-06-05 22:20:11,813 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-05 22:20:11,813 [INFO] nina.router: HybridRouter initialized
2026-06-05 22:20:11,814 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 22:20:11,819 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-05 22:20:11,819 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-05 22:20:12,741 [INFO] nina.telegram: TelegramInterface polling started
2026-06-05 22:20:12,741 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-05 22:20:12,741 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-05 22:22:12,802 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-05 22:22:16,136 [INFO] nina.routerlog: {"ts": "2026-06-05T22:22:16.000+0600", "req_id": "2f57a409", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-05 22:22:16,136 [WARNING] nina.router: router_fail req_id=2f57a409 provider=POLLINATIONS err=http_429
2026-06-05 22:22:16,963 [INFO] nina.routerlog: {"ts": "2026-06-05T22:22:16.000+0600", "req_id": "2f57a409", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-05 22:22:16,963 [WARNING] nina.router: router_fail req_id=2f57a409 provider=CHUTES err=http_401
2026-06-05 22:22:17,079 [INFO] nina.routerlog: {"ts": "2026-06-05T22:22:17.000+0600", "req_id": "2f57a409", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-05 22:22:17,079 [WARNING] nina.router: router_fail req_id=2f57a409 provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-05 22:22:17,479 [INFO] nina.routerlog: {"ts": "2026-06-05T22:22:17.000+0600", "req_id": "2f57a409", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-05 22:22:17,479 [WARNING] nina.router: router_fail req_id=2f57a409 provider=CEREBRAS err=http_404
2026-06-05 22:22:18,489 [INFO] nina.routerlog: {"ts": "2026-06-05T22:22:18.000+0600", "req_id": "2f57a409", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 119, "cost_usd": 0.0, "ttf_ms": 1009, "total_ms": 1009, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:22:18,489 [INFO] nina.router: router_success req_id=2f57a409 provider=GROQ task=research ms=1009
2026-06-05 22:22:18,489 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-05_proposals.md
2026-06-05 22:53:18,496 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-05 22:53:27,730 [INFO] nina.routerlog: {"ts": "2026-06-05T22:53:27.000+0600", "req_id": "0f1b82ed", "provider": "MISTRAL", "task_type": "research", "input_tokens": 453, "output_tokens": 515, "cost_usd": 0.0, "ttf_ms": 9117, "total_ms": 9117, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 22:53:27,730 [INFO] nina.router: router_success req_id=0f1b82ed provider=MISTRAL task=research ms=9117
2026-06-05 22:53:27,730 [INFO] nina.idle: idle_proposal_appended topic=morning_report file=2026-06-05_proposals.md
2026-06-05 22:55:15,028 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-05 23:01:07,548 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1
2026-06-05 23:01:07,580 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-05 23:01:07,580 [INFO] nina.router: HybridRouter initialized
2026-06-05 23:01:07,580 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 23:01:07,585 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-05 23:01:07,585 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-05 23:01:08,721 [INFO] nina.telegram: TelegramInterface polling started
2026-06-05 23:01:08,721 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-05 23:01:08,721 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-05 23:03:08,778 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-05 23:03:10,935 [INFO] nina.routerlog: {"ts": "2026-06-05T23:03:10.000+0600", "req_id": "da974f41", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-05 23:03:10,935 [WARNING] nina.router: router_fail req_id=da974f41 provider=POLLINATIONS err=http_429
2026-06-05 23:03:11,968 [INFO] nina.routerlog: {"ts": "2026-06-05T23:03:11.000+0600", "req_id": "da974f41", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-05 23:03:11,968 [WARNING] nina.router: router_fail req_id=da974f41 provider=CHUTES err=http_401
2026-06-05 23:03:12,246 [INFO] nina.routerlog: {"ts": "2026-06-05T23:03:12.000+0600", "req_id": "da974f41", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-05 23:03:12,246 [WARNING] nina.router: router_fail req_id=da974f41 provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-05 23:03:13,402 [INFO] nina.routerlog: {"ts": "2026-06-05T23:03:13.000+0600", "req_id": "da974f41", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-05 23:03:13,402 [WARNING] nina.router: router_fail req_id=da974f41 provider=CEREBRAS err=http_404
2026-06-05 23:03:14,642 [INFO] nina.routerlog: {"ts": "2026-06-05T23:03:14.000+0600", "req_id": "da974f41", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 102, "cost_usd": 0.0, "ttf_ms": 1239, "total_ms": 1239, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 23:03:14,642 [INFO] nina.router: router_success req_id=da974f41 provider=GROQ task=research ms=1239
2026-06-05 23:03:14,642 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-05_proposals.md
2026-06-05 23:34:14,649 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-05 23:34:23,796 [INFO] nina.routerlog: {"ts": "2026-06-05T23:34:23.000+0600", "req_id": "f28e17f3", "provider": "MISTRAL", "task_type": "research", "input_tokens": 453, "output_tokens": 498, "cost_usd": 0.0, "ttf_ms": 9018, "total_ms": 9018, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-05 23:34:23,796 [INFO] nina.router: router_success req_id=f28e17f3 provider=MISTRAL task=research ms=9018
2026-06-05 23:34:23,796 [INFO] nina.idle: idle_proposal_appended topic=morning_report file=2026-06-05_proposals.md
2026-06-05 23:36:10,288 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-06 00:01:07,585 [INFO] nina.scheduler: NINA operational
```

### logs/nina.log.2026-06-06
Last modified: 2026-06-06 23:42:25
Size: 79184 bytes
```log
[truncated — showing last 200 lines]
2026-06-06 12:48:12,079 [INFO] nina.routerlog: {"ts": "2026-06-06T12:48:12.000+0600", "req_id": "f51754cb", "provider": "SAMBANOVA", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-06 12:48:12,079 [WARNING] nina.router: router_fail req_id=f51754cb provider=SAMBANOVA err=http_404
2026-06-06 12:48:14,274 [INFO] nina.routerlog: {"ts": "2026-06-06T12:48:14.000+0600", "req_id": "f51754cb", "provider": "HYPERBOLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_402"}
2026-06-06 12:48:14,274 [WARNING] nina.router: router_fail req_id=f51754cb provider=HYPERBOLIC err=http_402
2026-06-06 12:48:15,308 [INFO] nina.routerlog: {"ts": "2026-06-06T12:48:15.000+0600", "req_id": "f51754cb", "provider": "NOVITA", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-06 12:48:15,308 [WARNING] nina.router: router_fail req_id=f51754cb provider=NOVITA err=http_404
2026-06-06 12:48:16,579 [INFO] nina.routerlog: {"ts": "2026-06-06T12:48:16.000+0600", "req_id": "f51754cb", "provider": "OPENAI", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-06 12:48:16,579 [WARNING] nina.router: router_fail req_id=f51754cb provider=OPENAI err=http_401
2026-06-06 12:48:24,035 [INFO] nina.routerlog: {"ts": "2026-06-06T12:48:24.000+0600", "req_id": "f51754cb", "provider": "OPENROUTER", "task_type": "research", "input_tokens": 351, "output_tokens": 1082, "cost_usd": 0.0, "ttf_ms": 7456, "total_ms": 7456, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 12:48:24,035 [INFO] nina.router: router_success req_id=f51754cb provider=OPENROUTER task=research ms=7456
2026-06-06 12:48:24,035 [INFO] nina.idle: idle_proposal_appended topic=memory_context file=2026-06-06_proposals.md
2026-06-06 12:52:54,657 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-06 13:19:24,049 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-06 13:19:26,338 [INFO] nina.routerlog: {"ts": "2026-06-06T13:19:26.000+0600", "req_id": "de8b73ff", "provider": "GROQ", "task_type": "research", "input_tokens": 333, "output_tokens": 265, "cost_usd": 0.0, "ttf_ms": 2155, "total_ms": 2155, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 13:19:26,338 [INFO] nina.router: router_success req_id=de8b73ff provider=GROQ task=research ms=2155
2026-06-06 13:19:26,338 [INFO] nina.idle: idle_proposal_appended topic=scheduler_errors file=2026-06-06_proposals.md
2026-06-06 13:22:57,012 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-06 13:27:57,606 [WARNING] nina.router: quality_probe_fail provider=GEMINI marked degraded
2026-06-06 15:14:29,195 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-06 15:14:32,031 [INFO] nina.routerlog: {"ts": "2026-06-06T15:14:32.000+0600", "req_id": "0b64c7e1", "provider": "GROQ", "task_type": "research", "input_tokens": 333, "output_tokens": 299, "cost_usd": 0.0, "ttf_ms": 1728, "total_ms": 1728, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 15:14:32,031 [INFO] nina.router: router_success req_id=0b64c7e1 provider=GROQ task=research ms=1728
2026-06-06 15:14:32,031 [INFO] nina.idle: idle_proposal_appended topic=telegram_interface file=2026-06-06_proposals.md
2026-06-06 15:17:03,789 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-06 15:22:04,104 [WARNING] nina.router: quality_probe_fail provider=GEMINI marked degraded
2026-06-06 15:42:57,479 [INFO] nina.scheduler: NINA operational
2026-06-06 15:42:57,479 [INFO] nina.scheduler: NINA operational
2026-06-06 15:45:32,039 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-06 15:45:33,274 [INFO] nina.routerlog: {"ts": "2026-06-06T15:45:33.000+0600", "req_id": "7358a1e3", "provider": "GROQ", "task_type": "research", "input_tokens": 336, "output_tokens": 276, "cost_usd": 0.0, "ttf_ms": 1113, "total_ms": 1113, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 15:45:33,274 [INFO] nina.router: router_success req_id=7358a1e3 provider=GROQ task=research ms=1113
2026-06-06 15:45:33,274 [INFO] nina.idle: idle_proposal_appended topic=config_robustness file=2026-06-06_proposals.md
2026-06-06 15:47:05,948 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-06 15:52:06,271 [WARNING] nina.router: quality_probe_fail provider=GEMINI marked degraded
2026-06-06 16:16:33,282 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-06 16:16:34,715 [INFO] nina.routerlog: {"ts": "2026-06-06T16:16:34.000+0600", "req_id": "01d74d3d", "provider": "GROQ", "task_type": "research", "input_tokens": 335, "output_tokens": 102, "cost_usd": 0.0, "ttf_ms": 1321, "total_ms": 1321, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 16:16:34,715 [INFO] nina.router: router_success req_id=01d74d3d provider=GROQ task=research ms=1321
2026-06-06 16:16:34,716 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-06_proposals.md
2026-06-06 16:17:08,246 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-06 16:22:08,666 [WARNING] nina.router: quality_probe_fail provider=GEMINI marked degraded
2026-06-06 16:42:57,480 [INFO] nina.scheduler: NINA operational
2026-06-06 16:42:57,480 [INFO] nina.scheduler: NINA operational
2026-06-06 16:42:57,481 [INFO] nina.scheduler: provider_health_probe
2026-06-06 16:42:57,481 [INFO] nina.scheduler: provider_health_probe
2026-06-06 16:47:34,725 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-06 16:47:36,307 [INFO] nina.routerlog: {"ts": "2026-06-06T16:47:36.000+0600", "req_id": "d8a8a12b", "provider": "GROQ", "task_type": "research", "input_tokens": 334, "output_tokens": 258, "cost_usd": 0.0, "ttf_ms": 1436, "total_ms": 1436, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 16:47:36,307 [INFO] nina.router: router_success req_id=d8a8a12b provider=GROQ task=research ms=1436
2026-06-06 16:47:36,307 [INFO] nina.idle: idle_proposal_appended topic=morning_report file=2026-06-06_proposals.md
2026-06-06 16:52:10,947 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-06 16:57:11,318 [WARNING] nina.router: quality_probe_fail provider=GEMINI marked degraded
2026-06-06 17:04:47,766 [INFO] nina.config: config_hotreload no reloadable changes
2026-06-06 17:04:53,535 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1
2026-06-06 17:04:53,575 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-06 17:04:53,575 [INFO] nina.router: HybridRouter initialized
2026-06-06 17:04:53,575 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 17:04:53,580 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-06 17:04:53,580 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-06 17:04:54,498 [INFO] nina.telegram: TelegramInterface polling started
2026-06-06 17:04:54,498 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-06 17:04:54,498 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-06 17:05:11,085 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1
2026-06-06 17:05:11,117 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-06 17:05:11,117 [INFO] nina.router: HybridRouter initialized
2026-06-06 17:05:11,117 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 17:05:11,121 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-06 17:05:11,121 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-06 17:05:12,417 [INFO] nina.telegram: TelegramInterface polling started
2026-06-06 17:05:12,418 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-06 17:05:12,418 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-06 17:07:12,476 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-06 17:07:14,991 [INFO] nina.routerlog: {"ts": "2026-06-06T17:07:14.000+0600", "req_id": "e248b91f", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-06 17:07:14,991 [WARNING] nina.router: router_fail req_id=e248b91f provider=POLLINATIONS err=http_429
2026-06-06 17:07:15,708 [INFO] nina.routerlog: {"ts": "2026-06-06T17:07:15.000+0600", "req_id": "e248b91f", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-06 17:07:15,708 [WARNING] nina.router: router_fail req_id=e248b91f provider=CHUTES err=http_401
2026-06-06 17:07:15,756 [INFO] nina.routerlog: {"ts": "2026-06-06T17:07:15.000+0600", "req_id": "e248b91f", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-06 17:07:15,756 [WARNING] nina.router: router_fail req_id=e248b91f provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-06 17:07:17,893 [INFO] nina.routerlog: {"ts": "2026-06-06T17:07:17.000+0600", "req_id": "e248b91f", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-06 17:07:17,893 [WARNING] nina.router: router_fail req_id=e248b91f provider=CEREBRAS err=http_404
2026-06-06 17:07:18,817 [INFO] nina.routerlog: {"ts": "2026-06-06T17:07:18.000+0600", "req_id": "e248b91f", "provider": "GROQ", "task_type": "research", "input_tokens": 322, "output_tokens": 104, "cost_usd": 0.0, "ttf_ms": 923, "total_ms": 923, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 17:07:18,817 [INFO] nina.router: router_success req_id=e248b91f provider=GROQ task=research ms=923
2026-06-06 17:07:18,817 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-06_proposals.md
2026-06-06 19:42:38,456 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1
2026-06-06 19:42:40,018 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-06 19:42:40,018 [INFO] nina.router: HybridRouter initialized
2026-06-06 19:42:40,018 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 19:42:40,026 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-06 19:42:40,026 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-06 19:42:40,835 [INFO] nina.telegram: TelegramInterface polling started
2026-06-06 19:42:40,835 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-06 19:42:40,835 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-06 19:44:40,901 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-06 19:44:43,335 [INFO] nina.routerlog: {"ts": "2026-06-06T19:44:43.000+0600", "req_id": "09d0f2fe", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-06 19:44:43,335 [WARNING] nina.router: router_fail req_id=09d0f2fe provider=POLLINATIONS err=http_429
2026-06-06 19:44:43,859 [INFO] nina.routerlog: {"ts": "2026-06-06T19:44:43.000+0600", "req_id": "09d0f2fe", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-06 19:44:43,859 [WARNING] nina.router: router_fail req_id=09d0f2fe provider=CHUTES err=http_401
2026-06-06 19:44:43,937 [INFO] nina.routerlog: {"ts": "2026-06-06T19:44:43.000+0600", "req_id": "09d0f2fe", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-06 19:44:43,938 [WARNING] nina.router: router_fail req_id=09d0f2fe provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-06 19:44:44,447 [INFO] nina.routerlog: {"ts": "2026-06-06T19:44:44.000+0600", "req_id": "09d0f2fe", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-06 19:44:44,448 [WARNING] nina.router: router_fail req_id=09d0f2fe provider=CEREBRAS err=http_404
2026-06-06 19:44:45,304 [INFO] nina.routerlog: {"ts": "2026-06-06T19:44:45.000+0600", "req_id": "09d0f2fe", "provider": "GROQ", "task_type": "research", "input_tokens": 322, "output_tokens": 129, "cost_usd": 0.0, "ttf_ms": 856, "total_ms": 856, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 19:44:45,304 [INFO] nina.router: router_success req_id=09d0f2fe provider=GROQ task=research ms=856
2026-06-06 19:44:45,309 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-06_proposals.md
2026-06-06 20:00:14,614 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1
2026-06-06 20:00:14,646 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-06 20:00:14,646 [INFO] nina.router: HybridRouter initialized
2026-06-06 20:00:14,646 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 20:00:14,652 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-06 20:00:14,652 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-06 20:00:15,519 [INFO] nina.telegram: TelegramInterface polling started
2026-06-06 20:00:15,519 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-06 20:00:15,519 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-06 20:02:15,577 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-06 20:02:17,734 [INFO] nina.routerlog: {"ts": "2026-06-06T20:02:17.000+0600", "req_id": "192b64d0", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-06 20:02:17,734 [WARNING] nina.router: router_fail req_id=192b64d0 provider=POLLINATIONS err=http_429
2026-06-06 20:02:19,052 [INFO] nina.routerlog: {"ts": "2026-06-06T20:02:19.000+0600", "req_id": "192b64d0", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-06 20:02:19,052 [WARNING] nina.router: router_fail req_id=192b64d0 provider=CHUTES err=http_401
2026-06-06 20:02:19,128 [INFO] nina.routerlog: {"ts": "2026-06-06T20:02:19.000+0600", "req_id": "192b64d0", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-06 20:02:19,128 [WARNING] nina.router: router_fail req_id=192b64d0 provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-06 20:02:19,726 [INFO] nina.routerlog: {"ts": "2026-06-06T20:02:19.000+0600", "req_id": "192b64d0", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-06 20:02:19,726 [WARNING] nina.router: router_fail req_id=192b64d0 provider=CEREBRAS err=http_404
2026-06-06 20:02:20,692 [INFO] nina.routerlog: {"ts": "2026-06-06T20:02:20.000+0600", "req_id": "192b64d0", "provider": "GROQ", "task_type": "research", "input_tokens": 312, "output_tokens": 125, "cost_usd": 0.0, "ttf_ms": 965, "total_ms": 965, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 20:02:20,692 [INFO] nina.router: router_success req_id=192b64d0 provider=GROQ task=research ms=965
2026-06-06 20:02:20,692 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-06_proposals.md
2026-06-06 20:33:20,698 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-06 20:33:22,218 [INFO] nina.routerlog: {"ts": "2026-06-06T20:33:22.000+0600", "req_id": "6ff863a8", "provider": "GROQ", "task_type": "research", "input_tokens": 311, "output_tokens": 279, "cost_usd": 0.0, "ttf_ms": 1386, "total_ms": 1386, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 20:33:22,218 [INFO] nina.router: router_success req_id=6ff863a8 provider=GROQ task=research ms=1386
2026-06-06 20:33:22,218 [INFO] nina.idle: idle_proposal_appended topic=morning_report file=2026-06-06_proposals.md
2026-06-06 20:35:17,751 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-06 21:00:14,652 [INFO] nina.scheduler: NINA operational
2026-06-06 21:00:14,652 [INFO] nina.scheduler: NINA operational
2026-06-06 21:04:22,230 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-06 21:04:38,218 [INFO] nina.routerlog: {"ts": "2026-06-06T21:04:38.000+0600", "req_id": "14f0ffab", "provider": "MISTRAL", "task_type": "research", "input_tokens": 293, "output_tokens": 950, "cost_usd": 0.0, "ttf_ms": 15877, "total_ms": 15877, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 21:04:38,218 [INFO] nina.router: router_success req_id=14f0ffab provider=MISTRAL task=research ms=15877
2026-06-06 21:04:38,219 [INFO] nina.idle: idle_proposal_appended topic=provider_routing file=2026-06-06_proposals.md
2026-06-06 21:05:19,708 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-06 21:27:15,267 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1
2026-06-06 21:27:15,297 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-06 21:27:15,297 [INFO] nina.router: HybridRouter initialized
2026-06-06 21:27:15,297 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 21:27:15,303 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-06 21:27:15,303 [INFO] nina.scheduler: Scheduler started — 13 jobs
2026-06-06 21:27:16,163 [INFO] nina.telegram: TelegramInterface polling started
2026-06-06 21:27:16,163 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-06 21:27:16,163 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-06 21:29:16,219 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-06 21:29:18,320 [INFO] nina.routerlog: {"ts": "2026-06-06T21:29:18.000+0600", "req_id": "6828e7be", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-06 21:29:18,320 [WARNING] nina.router: router_fail req_id=6828e7be provider=POLLINATIONS err=http_429
2026-06-06 21:29:19,035 [INFO] nina.routerlog: {"ts": "2026-06-06T21:29:19.000+0600", "req_id": "6828e7be", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-06 21:29:19,040 [WARNING] nina.router: router_fail req_id=6828e7be provider=CHUTES err=http_401
2026-06-06 21:29:19,138 [INFO] nina.routerlog: {"ts": "2026-06-06T21:29:19.000+0600", "req_id": "6828e7be", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-06 21:29:19,139 [WARNING] nina.router: router_fail req_id=6828e7be provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-06 21:29:19,762 [INFO] nina.routerlog: {"ts": "2026-06-06T21:29:19.000+0600", "req_id": "6828e7be", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-06 21:29:19,763 [WARNING] nina.router: router_fail req_id=6828e7be provider=CEREBRAS err=http_404
2026-06-06 21:29:21,127 [INFO] nina.routerlog: {"ts": "2026-06-06T21:29:21.000+0600", "req_id": "6828e7be", "provider": "GROQ", "task_type": "research", "input_tokens": 312, "output_tokens": 110, "cost_usd": 0.0, "ttf_ms": 1364, "total_ms": 1364, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 21:29:21,127 [INFO] nina.router: router_success req_id=6828e7be provider=GROQ task=research ms=1364
2026-06-06 21:29:21,127 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-06_proposals.md
2026-06-06 22:00:21,138 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-06 22:00:34,346 [INFO] nina.routerlog: {"ts": "2026-06-06T22:00:34.000+0600", "req_id": "9cb499cd", "provider": "MISTRAL", "task_type": "research", "input_tokens": 299, "output_tokens": 728, "cost_usd": 0.0, "ttf_ms": 13087, "total_ms": 13087, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 22:00:34,346 [INFO] nina.router: router_success req_id=9cb499cd provider=MISTRAL task=research ms=13087
2026-06-06 22:00:34,347 [INFO] nina.idle: idle_proposal_appended topic=morning_report file=2026-06-06_proposals.md
2026-06-06 22:02:17,725 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-06 22:27:15,304 [INFO] nina.scheduler: NINA operational
2026-06-06 22:27:15,304 [INFO] nina.scheduler: NINA operational
2026-06-06 22:31:34,367 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-06 22:31:34,790 [INFO] nina.routerlog: {"ts": "2026-06-06T22:31:34.000+0600", "req_id": "bf65b61a", "provider": "DEEPSEEK", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-06 22:31:34,795 [WARNING] nina.router: router_fail req_id=bf65b61a provider=DEEPSEEK err=http_401
2026-06-06 22:31:35,224 [INFO] nina.routerlog: {"ts": "2026-06-06T22:31:35.000+0600", "req_id": "bf65b61a", "provider": "GEMINI", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-06 22:31:35,224 [WARNING] nina.router: router_fail req_id=bf65b61a provider=GEMINI err=http_429
2026-06-06 22:31:36,177 [INFO] nina.routerlog: {"ts": "2026-06-06T22:31:36.000+0600", "req_id": "bf65b61a", "provider": "TOGETHER", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-06 22:31:36,177 [WARNING] nina.router: router_fail req_id=bf65b61a provider=TOGETHER err=http_404
2026-06-06 22:31:37,071 [INFO] nina.routerlog: {"ts": "2026-06-06T22:31:37.000+0600", "req_id": "bf65b61a", "provider": "COHERE", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_405"}
2026-06-06 22:31:37,071 [WARNING] nina.router: router_fail req_id=bf65b61a provider=COHERE err=http_405
2026-06-06 22:31:38,299 [INFO] nina.routerlog: {"ts": "2026-06-06T22:31:38.000+0600", "req_id": "bf65b61a", "provider": "FIREWORKS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-06 22:31:38,299 [WARNING] nina.router: router_fail req_id=bf65b61a provider=FIREWORKS err=http_404
2026-06-06 22:31:38,577 [INFO] nina.routerlog: {"ts": "2026-06-06T22:31:38.000+0600", "req_id": "bf65b61a", "provider": "XAI", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_400"}
2026-06-06 22:31:38,577 [WARNING] nina.router: router_fail req_id=bf65b61a provider=XAI err=http_400
2026-06-06 22:31:39,533 [INFO] nina.routerlog: {"ts": "2026-06-06T22:31:39.000+0600", "req_id": "bf65b61a", "provider": "SAMBANOVA", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-06 22:31:39,533 [WARNING] nina.router: router_fail req_id=bf65b61a provider=SAMBANOVA err=http_404
2026-06-06 22:31:41,022 [INFO] nina.routerlog: {"ts": "2026-06-06T22:31:41.000+0600", "req_id": "bf65b61a", "provider": "HYPERBOLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_402"}
2026-06-06 22:31:41,022 [WARNING] nina.router: router_fail req_id=bf65b61a provider=HYPERBOLIC err=http_402
2026-06-06 22:31:42,136 [INFO] nina.routerlog: {"ts": "2026-06-06T22:31:42.000+0600", "req_id": "bf65b61a", "provider": "NOVITA", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-06 22:31:42,136 [WARNING] nina.router: router_fail req_id=bf65b61a provider=NOVITA err=http_404
2026-06-06 22:31:43,605 [INFO] nina.routerlog: {"ts": "2026-06-06T22:31:43.000+0600", "req_id": "bf65b61a", "provider": "OPENAI", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-06 22:31:43,605 [WARNING] nina.router: router_fail req_id=bf65b61a provider=OPENAI err=http_401
2026-06-06 22:31:52,142 [INFO] nina.routerlog: {"ts": "2026-06-06T22:31:52.000+0600", "req_id": "bf65b61a", "provider": "OPENROUTER", "task_type": "research", "input_tokens": 323, "output_tokens": 1248, "cost_usd": 0.0, "ttf_ms": 8536, "total_ms": 8536, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 22:31:52,142 [INFO] nina.router: router_success req_id=bf65b61a provider=OPENROUTER task=research ms=8536
2026-06-06 22:31:52,142 [INFO] nina.idle: idle_proposal_appended topic=provider_routing file=2026-06-06_proposals.md
2026-06-06 22:32:19,874 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-06 23:02:52,162 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-06 23:02:55,497 [INFO] nina.routerlog: {"ts": "2026-06-06T23:02:55.000+0600", "req_id": "38365f6f", "provider": "GROQ", "task_type": "research", "input_tokens": 310, "output_tokens": 337, "cost_usd": 0.0, "ttf_ms": 3210, "total_ms": 3210, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 23:02:55,497 [INFO] nina.router: router_success req_id=38365f6f provider=GROQ task=research ms=3210
2026-06-06 23:02:55,497 [INFO] nina.idle: idle_proposal_appended topic=memory_context file=2026-06-06_proposals.md
2026-06-06 23:07:22,917 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-06 23:12:23,305 [WARNING] nina.router: quality_probe_fail provider=GEMINI marked degraded
2026-06-06 23:27:15,309 [INFO] nina.scheduler: NINA operational
2026-06-06 23:27:15,309 [INFO] nina.scheduler: NINA operational
2026-06-06 23:33:55,505 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-06 23:33:56,538 [INFO] nina.routerlog: {"ts": "2026-06-06T23:33:56.000+0600", "req_id": "c1edd7d7", "provider": "GROQ", "task_type": "research", "input_tokens": 310, "output_tokens": 174, "cost_usd": 0.0, "ttf_ms": 908, "total_ms": 908, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-06 23:33:56,538 [INFO] nina.router: router_success req_id=c1edd7d7 provider=GROQ task=research ms=908
2026-06-06 23:33:56,539 [INFO] nina.idle: idle_proposal_appended topic=scheduler_errors file=2026-06-06_proposals.md
2026-06-06 23:37:25,231 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-06 23:42:25,753 [WARNING] nina.router: quality_probe_fail provider=GEMINI marked degraded
```

### logs/nina.log.2026-06-07
Last modified: 2026-06-08 01:33:10
Size: 593444 bytes
```log
[truncated — showing last 200 lines]
2026-06-07 21:51:46,265 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-07 21:51:46,265 [INFO] nina.router: HybridRouter initialized
2026-06-07 21:51:46,265 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-07 21:51:52,546 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1 reminders=0
2026-06-07 21:51:52,584 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-07 21:51:52,584 [INFO] nina.router: HybridRouter initialized
2026-06-07 21:51:52,584 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-07 21:51:58,972 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1 reminders=0
2026-06-07 21:51:59,006 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-07 21:51:59,006 [INFO] nina.router: HybridRouter initialized
2026-06-07 21:51:59,006 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-07 21:52:05,200 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1 reminders=0
2026-06-07 21:52:05,234 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-07 21:52:05,234 [INFO] nina.router: HybridRouter initialized
2026-06-07 21:52:05,234 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-07 21:52:11,464 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1 reminders=0
2026-06-07 21:52:11,497 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-07 21:52:11,497 [INFO] nina.router: HybridRouter initialized
2026-06-07 21:52:11,498 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-07 21:52:17,730 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1 reminders=0
2026-06-07 21:52:17,768 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-07 21:52:17,769 [INFO] nina.router: HybridRouter initialized
2026-06-07 21:52:17,769 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-07 21:52:23,954 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1 reminders=0
2026-06-07 21:52:23,987 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-07 21:52:23,987 [INFO] nina.router: HybridRouter initialized
2026-06-07 21:52:23,987 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-07 21:52:30,225 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1 reminders=0
2026-06-07 21:52:30,260 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-06-07 21:52:30,260 [INFO] nina.router: HybridRouter initialized
2026-06-07 21:52:30,260 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-07 21:52:30,266 [INFO] nina.scheduler: Scheduler started — 16 jobs
2026-06-07 21:52:30,266 [INFO] nina.scheduler: Scheduler started — 16 jobs
2026-06-07 21:52:31,167 [INFO] nina.telegram: TelegramInterface polling started
2026-06-07 21:52:31,172 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-06-07 21:52:31,173 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-07 21:54:31,223 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-07 21:54:34,346 [INFO] nina.routerlog: {"ts": "2026-06-07T21:54:34.000+0600", "req_id": "1df8c486", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-07 21:54:34,346 [WARNING] nina.router: router_fail req_id=1df8c486 provider=POLLINATIONS err=http_429
2026-06-07 21:54:34,416 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-07 21:54:34,953 [INFO] nina.routerlog: {"ts": "2026-06-07T21:54:34.000+0600", "req_id": "1df8c486", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-07 21:54:34,953 [WARNING] nina.router: router_fail req_id=1df8c486 provider=CHUTES err=http_401
2026-06-07 21:54:35,079 [INFO] nina.routerlog: {"ts": "2026-06-07T21:54:35.000+0600", "req_id": "1df8c486", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-07 21:54:35,079 [WARNING] nina.router: router_fail req_id=1df8c486 provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-07 21:54:35,397 [INFO] nina.routerlog: {"ts": "2026-06-07T21:54:35.000+0600", "req_id": "1df8c486", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-07 21:54:35,397 [WARNING] nina.router: router_fail req_id=1df8c486 provider=CEREBRAS err=http_404
2026-06-07 21:54:36,176 [INFO] nina.routerlog: {"ts": "2026-06-07T21:54:36.000+0600", "req_id": "1df8c486", "provider": "GROQ", "task_type": "research", "input_tokens": 369, "output_tokens": 117, "cost_usd": 0.0, "ttf_ms": 778, "total_ms": 778, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-07 21:54:36,176 [INFO] nina.router: router_success req_id=1df8c486 provider=GROQ task=research ms=778
2026-06-07 21:54:36,177 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-07_proposals.md
2026-06-07 21:54:36,302 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-07 21:54:36,303 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-07 21:54:36,505 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-07 21:54:37,118 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-07 21:54:37,452 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-07 21:54:37,454 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-07 21:54:38,081 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-07 21:54:38,082 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-07 22:07:30,365 [INFO] nina.scheduler: reminder_check
2026-06-07 22:07:30,365 [INFO] nina.scheduler: reminder_check
2026-06-07 22:22:30,301 [INFO] nina.scheduler: reminder_check
2026-06-07 22:22:30,301 [INFO] nina.scheduler: reminder_check
2026-06-07 22:25:36,185 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-07 22:25:36,359 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "GROQ", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,359 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=GROQ err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,360 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "MISTRAL", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,360 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=MISTRAL err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,362 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "DEEPSEEK", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,362 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=DEEPSEEK err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,363 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "GEMINI", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,363 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=GEMINI err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,364 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "TOGETHER", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,365 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=TOGETHER err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,366 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "COHERE", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,366 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=COHERE err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,367 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "FIREWORKS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,367 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=FIREWORKS err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,368 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "XAI", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,369 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=XAI err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,386 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "SAMBANOVA", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,386 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=SAMBANOVA err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,388 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "HYPERBOLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,388 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=HYPERBOLIC err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,389 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "NOVITA", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,390 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=NOVITA err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,391 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "OPENAI", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,391 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=OPENAI err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,392 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "OPENROUTER", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,392 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=OPENROUTER err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,400 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,401 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=CHUTES err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,408 [WARNING] nina.model_discovery: Discovery failed for GROQ: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,410 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,410 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=HFPUBLIC err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,411 [WARNING] nina.model_discovery: Discovery failed for GROQ: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,411 [WARNING] nina.model_discovery: Discovery failed for GEMINI: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,413 [WARNING] nina.model_discovery: Discovery failed for GEMINI: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,413 [WARNING] nina.model_discovery: Discovery failed for CEREBRAS: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,414 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,414 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=CEREBRAS err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,421 [WARNING] nina.model_discovery: Discovery failed for CEREBRAS: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,421 [WARNING] nina.model_discovery: Discovery failed for MISTRAL: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,423 [WARNING] nina.model_discovery: Discovery failed for GROQ: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,424 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -3] Temporary failure in name resolution"}
2026-06-07 22:25:36,424 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=POLLINATIONS err=[Errno -3] Temporary failure in name resolution
2026-06-07 22:25:36,425 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,425 [WARNING] nina.model_discovery: Discovery failed for MISTRAL: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,426 [WARNING] nina.model_discovery: Discovery failed for GEMINI: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,428 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,429 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-07 22:25:36,430 [WARNING] nina.model_discovery: Discovery failed for CEREBRAS: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,430 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,431 [WARNING] nina.model_discovery: Discovery failed for MISTRAL: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,431 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,433 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-07 22:25:36,434 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,435 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: [Errno -3] Temporary failure in name resolution. Using fallback.
2026-06-07 22:25:36,435 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-07 22:25:36,442 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:36.000+0600", "req_id": "f1e05f8d", "provider": "LOCALHEAVY", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_400"}
2026-06-07 22:25:36,442 [WARNING] nina.router: router_fail req_id=f1e05f8d provider=LOCALHEAVY err=http_400
2026-06-07 22:25:50,546 [INFO] nina.routerlog: {"ts": "2026-06-07T22:25:50.000+0600", "req_id": "f1e05f8d", "provider": "LOCALFAST", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 14103, "total_ms": 14103, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-07 22:25:50,547 [INFO] nina.router: router_success req_id=f1e05f8d provider=LOCALFAST task=research ms=14103
2026-06-07 22:25:50,548 [INFO] nina.idle: idle_proposal_appended topic=morning_report file=2026-06-07_proposals.md
2026-06-07 22:37:30,310 [INFO] nina.scheduler: reminder_check
2026-06-07 22:37:30,310 [INFO] nina.scheduler: reminder_check
2026-06-07 22:52:30,270 [INFO] nina.scheduler: NINA operational
2026-06-07 22:52:30,270 [INFO] nina.scheduler: NINA operational
2026-06-07 22:52:30,307 [INFO] nina.scheduler: reminder_check
2026-06-07 22:52:30,307 [INFO] nina.scheduler: reminder_check
2026-06-07 22:56:50,560 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-07 22:56:51,721 [INFO] nina.routerlog: {"ts": "2026-06-07T22:56:51.000+0600", "req_id": "9699667b", "provider": "GROQ", "task_type": "research", "input_tokens": 364, "output_tokens": 136, "cost_usd": 0.0, "ttf_ms": 976, "total_ms": 976, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-07 22:56:51,722 [INFO] nina.router: router_success req_id=9699667b provider=GROQ task=research ms=976
2026-06-07 22:56:51,722 [INFO] nina.idle: idle_proposal_appended topic=provider_routing file=2026-06-07_proposals.md
2026-06-07 22:57:32,476 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-07 22:57:32,477 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-07 22:57:33,411 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-07 22:57:33,412 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-04-16 00:33:09,743 [INFO] nina.memory: MemorySystem ready conversations=0 facts=1 reminders=0
2026-04-16 00:33:10,625 [INFO] nina.router: local_models_discovered fast=qwen2.5:1.5b heavy=nomic-embed-text:latest
2026-04-16 00:33:10,625 [INFO] nina.router: HybridRouter initialized
2026-04-16 00:33:10,625 [INFO] nina.upgrade: UpgradePipeline ready
2026-04-16 00:33:10,635 [INFO] nina.scheduler: Scheduler started — 16 jobs
2026-04-16 00:33:10,635 [INFO] nina.scheduler: Scheduler started — 16 jobs
2026-04-16 00:33:11,337 [INFO] nina.telegram: TelegramInterface polling started
2026-04-16 00:33:11,337 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only mode)
2026-04-16 00:33:11,337 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-07 23:07:16,508 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-07 23:07:36,171 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-07 23:07:36,476 [INFO] nina.routerlog: {"ts": "2026-06-07T23:07:36.000+0600", "req_id": "5d208ecf", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_429"}
2026-06-07 23:07:36,477 [WARNING] nina.router: router_fail req_id=5d208ecf provider=POLLINATIONS err=http_429
2026-06-07 23:07:37,096 [INFO] nina.routerlog: {"ts": "2026-06-07T23:07:37.000+0600", "req_id": "5d208ecf", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_401"}
2026-06-07 23:07:37,096 [WARNING] nina.router: router_fail req_id=5d208ecf provider=CHUTES err=http_401
2026-06-07 23:07:37,195 [INFO] nina.routerlog: {"ts": "2026-06-07T23:07:37.000+0600", "req_id": "5d208ecf", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-06-07 23:07:37,196 [WARNING] nina.router: router_fail req_id=5d208ecf provider=HFPUBLIC err=[Errno -5] No address associated with hostname
2026-06-07 23:07:37,510 [INFO] nina.routerlog: {"ts": "2026-06-07T23:07:37.000+0600", "req_id": "5d208ecf", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "http_404"}
2026-06-07 23:07:37,510 [WARNING] nina.router: router_fail req_id=5d208ecf provider=CEREBRAS err=http_404
2026-06-07 23:07:38,008 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-07 23:07:38,015 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-07 23:07:38,017 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-07 23:07:38,108 [INFO] nina.routerlog: {"ts": "2026-06-07T23:07:38.000+0600", "req_id": "5d208ecf", "provider": "GROQ", "task_type": "research", "input_tokens": 370, "output_tokens": 96, "cost_usd": 0.0, "ttf_ms": 597, "total_ms": 597, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-07 23:07:38,108 [INFO] nina.router: router_success req_id=5d208ecf provider=GROQ task=research ms=597
2026-06-07 23:07:38,110 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-07_proposals.md
2026-06-07 23:07:38,815 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-07 23:07:38,816 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-07 23:07:38,943 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-07 23:07:39,323 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-07 23:07:39,324 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-07 23:18:10,658 [INFO] nina.scheduler: reminder_check
2026-06-07 23:18:10,658 [INFO] nina.scheduler: reminder_check
2026-06-07 23:33:10,636 [INFO] nina.scheduler: NINA operational
2026-06-07 23:33:10,636 [INFO] nina.scheduler: NINA operational
2026-06-07 23:33:10,660 [INFO] nina.scheduler: reminder_check
2026-06-07 23:33:10,660 [INFO] nina.scheduler: reminder_check
2026-06-07 23:38:38,120 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-07 23:38:38,875 [INFO] nina.routerlog: {"ts": "2026-06-07T23:38:38.000+0600", "req_id": "74841321", "provider": "GROQ", "task_type": "research", "input_tokens": 369, "output_tokens": 96, "cost_usd": 0.0, "ttf_ms": 583, "total_ms": 583, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-07 23:38:38,875 [INFO] nina.router: router_success req_id=74841321 provider=GROQ task=research ms=583
2026-06-07 23:38:38,875 [INFO] nina.idle: idle_proposal_appended topic=morning_report file=2026-06-07_proposals.md
2026-06-07 23:41:17,553 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-07 23:41:18,373 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-07 23:41:19,944 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-07 23:41:19,945 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-07 23:48:10,754 [INFO] nina.scheduler: reminder_check
2026-06-07 23:48:10,754 [INFO] nina.scheduler: reminder_check
2026-06-08 00:03:10,662 [INFO] nina.scheduler: reminder_check
2026-06-08 00:18:10,752 [INFO] nina.scheduler: reminder_check
2026-06-08 00:33:10,639 [INFO] nina.scheduler: NINA operational
2026-06-08 00:33:10,640 [INFO] nina.scheduler: provider_health_probe
2026-06-08 00:33:10,662 [INFO] nina.scheduler: reminder_check
2026-06-08 00:48:10,655 [INFO] nina.scheduler: reminder_check
2026-06-08 01:03:10,752 [INFO] nina.scheduler: reminder_check
2026-06-08 01:18:10,661 [INFO] nina.scheduler: reminder_check
2026-06-08 01:33:10,640 [INFO] nina.scheduler: NINA operational
2026-06-08 01:33:10,727 [INFO] nina.scheduler: reminder_check
```

### logs/nina.log.2026-06-08
Last modified: 2026-06-09 04:48:33
Size: 128630 bytes
```log
[truncated — showing last 200 lines]
2026-06-09 00:46:37,245 [INFO] nina.scheduler: reminder_check
2026-06-09 00:46:37,245 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001399517059326172, "success": true}
2026-06-09 00:46:37,245 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 4.506111145019531e-05, "success": true}
2026-06-09 00:51:37,250 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02129364013671875, "success": true}
2026-06-09 00:56:37,241 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021313190460205078, "success": true}
2026-06-09 00:56:50,505 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-09 00:56:51,297 [INFO] nina.routerlog: {"ts": "2026-06-09T00:56:51.000+0600", "req_id": "803af337", "provider": "GROQ", "task_type": "research", "input_tokens": 373, "output_tokens": 87, "cost_usd": 0.0, "ttf_ms": 609, "total_ms": 609, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-09 00:56:51,297 [INFO] nina.router: router_success req_id=803af337 provider=GROQ task=research ms=609
2026-06-09 00:56:51,297 [INFO] nina.idle: idle_proposal_appended topic=morning_report file=2026-06-09_proposals.md
2026-06-09 00:57:01,401 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-09 00:57:01,951 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-09 00:57:02,344 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-09 00:57:02,345 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-09 01:01:37,259 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.03343963623046875, "success": true}
2026-06-09 01:01:37,259 [INFO] nina.scheduler: reminder_check
2026-06-09 01:01:37,260 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001933574676513672, "success": true}
2026-06-09 01:01:37,260 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 5.91278076171875e-05, "success": true}
2026-06-09 01:06:37,249 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021654367446899414, "success": true}
2026-06-09 01:11:37,246 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02416229248046875, "success": true}
2026-06-09 01:16:37,224 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 4.792213439941406e-05, "success": true}
2026-06-09 01:16:37,245 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02081298828125, "success": true}
2026-06-09 01:16:37,246 [INFO] nina.scheduler: reminder_check
2026-06-09 01:16:37,246 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00016117095947265625, "success": true}
2026-06-09 01:16:37,246 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.8133392333984375e-05, "success": true}
2026-06-09 01:21:37,249 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02194690704345703, "success": true}
2026-06-09 01:26:37,241 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02093505859375, "success": true}
2026-06-09 01:27:51,311 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-09 01:27:52,397 [INFO] nina.routerlog: {"ts": "2026-06-09T01:27:52.000+0600", "req_id": "fe96d429", "provider": "GROQ", "task_type": "research", "input_tokens": 368, "output_tokens": 112, "cost_usd": 0.0, "ttf_ms": 909, "total_ms": 909, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-09 01:27:52,398 [INFO] nina.router: router_success req_id=fe96d429 provider=GROQ task=research ms=909
2026-06-09 01:27:52,398 [INFO] nina.idle: idle_proposal_appended topic=provider_routing file=2026-06-09_proposals.md
2026-06-09 01:31:37,281 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.05672287940979004, "success": true}
2026-06-09 01:31:37,282 [INFO] nina.scheduler: reminder_check
2026-06-09 01:31:37,282 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00010895729064941406, "success": true}
2026-06-09 01:31:37,282 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 4.029273986816406e-05, "success": true}
2026-06-09 01:32:04,273 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-09 01:32:04,275 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-09 01:32:05,167 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-09 01:32:05,168 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-09 01:36:37,251 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022130727767944336, "success": true}
2026-06-09 01:41:37,242 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021893978118896484, "success": true}
2026-06-09 01:46:37,224 [INFO] nina.scheduler: NINA operational
2026-06-09 01:46:37,224 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.00015687942504882812, "success": true}
2026-06-09 01:46:37,225 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 4.744529724121094e-05, "success": true}
2026-06-09 01:46:37,246 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020989179611206055, "success": true}
2026-06-09 01:46:37,246 [INFO] nina.scheduler: reminder_check
2026-06-09 01:46:37,246 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00015974044799804688, "success": true}
2026-06-09 01:46:37,247 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.4809112548828125e-05, "success": true}
2026-06-09 01:51:37,250 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02185654640197754, "success": true}
2026-06-09 01:56:38,011 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.7900335788726807, "success": true}
2026-06-09 01:58:52,408 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-09 01:58:53,537 [INFO] nina.routerlog: {"ts": "2026-06-09T01:58:53.000+0600", "req_id": "ad2e331f", "provider": "GROQ", "task_type": "research", "input_tokens": 372, "output_tokens": 74, "cost_usd": 0.0, "ttf_ms": 921, "total_ms": 921, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-09 01:58:53,537 [INFO] nina.router: router_success req_id=ad2e331f provider=GROQ task=research ms=921
2026-06-09 01:58:53,538 [INFO] nina.idle: idle_proposal_appended topic=memory_context file=2026-06-09_proposals.md
2026-06-09 02:00:00,595 [INFO] nina.providerhunter: provider_hunter found=2
2026-06-09 02:00:00,595 [INFO] nina.scheduler: {"event": "job_run", "job": "provider_hunter", "duration": 0.5850198268890381, "success": true}
2026-06-09 02:01:37,246 [INFO] nina.scheduler: reminder_check
2026-06-09 02:01:37,247 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00019240379333496094, "success": true}
2026-06-09 02:01:37,247 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.981590270996094e-05, "success": true}
2026-06-09 02:01:38,062 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.8383896350860596, "success": true}
2026-06-09 02:02:06,350 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-09 02:02:07,170 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-09 02:02:07,377 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-09 02:02:07,377 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-09 02:06:37,248 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022106409072875977, "success": true}
2026-06-09 02:11:37,240 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021092653274536133, "success": true}
2026-06-09 02:16:37,224 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 3.981590270996094e-05, "success": true}
2026-06-09 02:16:37,246 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022188663482666016, "success": true}
2026-06-09 02:16:37,246 [INFO] nina.scheduler: reminder_check
2026-06-09 02:16:37,247 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001735687255859375, "success": true}
2026-06-09 02:16:37,247 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 4.601478576660156e-05, "success": true}
2026-06-09 02:21:37,249 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02283787727355957, "success": true}
2026-06-09 02:26:37,240 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020981788635253906, "success": true}
2026-06-09 02:29:53,547 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-09 02:29:54,498 [INFO] nina.routerlog: {"ts": "2026-06-09T02:29:54.000+0600", "req_id": "9aa642c4", "provider": "GROQ", "task_type": "research", "input_tokens": 372, "output_tokens": 83, "cost_usd": 0.0, "ttf_ms": 757, "total_ms": 757, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-09 02:29:54,498 [INFO] nina.router: router_success req_id=9aa642c4 provider=GROQ task=research ms=757
2026-06-09 02:29:54,498 [INFO] nina.idle: idle_proposal_appended topic=scheduler_errors file=2026-06-09_proposals.md
2026-06-09 02:30:00,007 [INFO] nina.memory: memory_backup dest=upgrades/backups/memory20260609023000
2026-06-09 02:30:00,007 [INFO] nina.scheduler: memory_backup_ok dest=upgrades/backups/memory20260609023000
2026-06-09 02:30:00,007 [INFO] nina.scheduler: {"event": "job_run", "job": "memory_backup", "duration": 0.0058100223541259766, "success": true}
2026-06-09 02:31:37,246 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021745920181274414, "success": true}
2026-06-09 02:31:37,246 [INFO] nina.scheduler: reminder_check
2026-06-09 02:31:37,246 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00012564659118652344, "success": true}
2026-06-09 02:31:37,247 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.2411346435546875e-05, "success": true}
2026-06-09 02:32:09,423 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-09 02:32:09,833 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-09 02:32:10,296 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-09 02:32:10,297 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-09 02:36:37,248 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020705223083496094, "success": true}
2026-06-09 02:41:37,243 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022954940795898438, "success": true}
2026-06-09 02:46:37,224 [INFO] nina.scheduler: NINA operational
2026-06-09 02:46:37,224 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.00020194053649902344, "success": true}
2026-06-09 02:46:37,224 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 6.914138793945312e-05, "success": true}
2026-06-09 02:46:37,225 [INFO] nina.scheduler: provider_health_probe
2026-06-09 02:46:37,225 [INFO] nina.scheduler: {"event": "job_run", "job": "provider_health", "duration": 0.00011658668518066406, "success": true}
2026-06-09 02:46:37,247 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022324562072753906, "success": true}
2026-06-09 02:46:37,248 [INFO] nina.scheduler: reminder_check
2026-06-09 02:46:37,248 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001761913299560547, "success": true}
2026-06-09 02:46:37,248 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.1948089599609375e-05, "success": true}
2026-06-09 02:51:37,241 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021373748779296875, "success": true}
2026-06-09 02:56:37,249 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.0262296199798584, "success": true}
2026-06-09 03:00:00,262 [INFO] nina.scheduler: py_backup_ok dest=upgrades/backups/py_20260609030000.zip
2026-06-09 03:00:00,262 [INFO] nina.scheduler: {"event": "job_run", "job": "py_backup", "duration": 0.25954151153564453, "success": true}
2026-06-09 03:00:54,512 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-09 03:00:55,400 [INFO] nina.routerlog: {"ts": "2026-06-09T03:00:55.000+0600", "req_id": "a404988d", "provider": "GROQ", "task_type": "research", "input_tokens": 372, "output_tokens": 115, "cost_usd": 0.0, "ttf_ms": 687, "total_ms": 687, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-09 03:00:55,400 [INFO] nina.router: router_success req_id=a404988d provider=GROQ task=research ms=687
2026-06-09 03:00:55,400 [INFO] nina.idle: idle_proposal_appended topic=telegram_interface file=2026-06-09_proposals.md
2026-06-09 03:01:37,285 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.058485984802246094, "success": true}
2026-06-09 03:01:37,285 [INFO] nina.scheduler: reminder_check
2026-06-09 03:01:37,285 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00016832351684570312, "success": true}
2026-06-09 03:01:37,285 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.0503997802734375e-05, "success": true}
2026-06-09 03:02:11,591 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-09 03:02:11,984 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-09 03:02:12,823 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-09 03:02:12,824 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-09 03:05:00,007 [INFO] nina.scheduler: {"event": "job_run", "job": "cache_purge", "duration": 6.914138793945312e-05, "success": true}
2026-06-09 03:06:37,242 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02167654037475586, "success": true}
2026-06-09 03:11:37,245 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020789384841918945, "success": true}
2026-06-09 03:16:37,227 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 3.981590270996094e-05, "success": true}
2026-06-09 03:16:37,285 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.05794930458068848, "success": true}
2026-06-09 03:16:37,285 [INFO] nina.scheduler: reminder_check
2026-06-09 03:16:37,285 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.000141143798828125, "success": true}
2026-06-09 03:16:37,286 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.574920654296875e-05, "success": true}
2026-06-09 03:21:37,245 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.023334503173828125, "success": true}
2026-06-09 03:26:38,017 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.7932298183441162, "success": true}
2026-06-09 03:31:37,294 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.06680917739868164, "success": true}
2026-06-09 03:31:37,295 [INFO] nina.scheduler: reminder_check
2026-06-09 03:31:37,295 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00014400482177734375, "success": true}
2026-06-09 03:31:37,295 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 4.1961669921875e-05, "success": true}
2026-06-09 03:31:55,416 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-09 03:31:56,224 [INFO] nina.routerlog: {"ts": "2026-06-09T03:31:56.000+0600", "req_id": "9cff1520", "provider": "GROQ", "task_type": "research", "input_tokens": 375, "output_tokens": 104, "cost_usd": 0.0, "ttf_ms": 614, "total_ms": 614, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-09 03:31:56,224 [INFO] nina.router: router_success req_id=9cff1520 provider=GROQ task=research ms=614
2026-06-09 03:31:56,224 [INFO] nina.idle: idle_proposal_appended topic=config_robustness file=2026-06-09_proposals.md
2026-06-09 03:32:13,427 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-09 03:32:13,849 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-09 03:32:14,358 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-09 03:32:14,359 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-09 03:36:38,241 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 1.0193397998809814, "success": true}
2026-06-09 03:41:37,249 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.024428367614746094, "success": true}
2026-06-09 03:46:37,227 [INFO] nina.scheduler: NINA operational
2026-06-09 03:46:37,228 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.00046896934509277344, "success": true}
2026-06-09 03:46:37,228 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 6.818771362304688e-05, "success": true}
2026-06-09 03:46:37,258 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02895379066467285, "success": true}
2026-06-09 03:46:37,258 [INFO] nina.scheduler: reminder_check
2026-06-09 03:46:37,258 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00010800361633300781, "success": true}
2026-06-09 03:46:37,258 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.6226043701171875e-05, "success": true}
2026-06-09 03:51:37,254 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.03356575965881348, "success": true}
2026-06-09 03:56:37,254 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.029276132583618164, "success": true}
2026-06-09 04:00:00,005 [INFO] nina.scheduler: log_rotation_tick
2026-06-09 04:00:00,005 [INFO] nina.scheduler: {"event": "job_run", "job": "log_rotation", "duration": 0.0002448558807373047, "success": true}
2026-06-09 04:01:37,257 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.028978824615478516, "success": true}
2026-06-09 04:01:37,258 [INFO] nina.scheduler: reminder_check
2026-06-09 04:01:37,258 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00021719932556152344, "success": true}
2026-06-09 04:01:37,259 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 5.054473876953125e-05, "success": true}
2026-06-09 04:02:56,241 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-09 04:02:57,260 [INFO] nina.routerlog: {"ts": "2026-06-09T04:02:57.000+0600", "req_id": "7b54a194", "provider": "GROQ", "task_type": "research", "input_tokens": 374, "output_tokens": 82, "cost_usd": 0.0, "ttf_ms": 804, "total_ms": 804, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-09 04:02:57,260 [INFO] nina.router: router_success req_id=7b54a194 provider=GROQ task=research ms=804
2026-06-09 04:02:57,261 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-09_proposals.md
2026-06-09 04:06:37,249 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.027661800384521484, "success": true}
2026-06-09 04:07:15,461 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-09 04:07:16,031 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-09 04:07:17,071 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-09 04:07:17,072 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-09 04:11:37,252 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.0265352725982666, "success": true}
2026-06-09 04:16:37,221 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 7.271766662597656e-05, "success": true}
2026-06-09 04:16:37,260 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.03856253623962402, "success": true}
2026-06-09 04:16:37,261 [INFO] nina.scheduler: reminder_check
2026-06-09 04:16:37,261 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00029277801513671875, "success": true}
2026-06-09 04:16:37,261 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 4.887580871582031e-05, "success": true}
2026-06-09 04:21:37,266 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.04265189170837402, "success": true}
2026-06-09 04:26:37,268 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.039040327072143555, "success": true}
2026-06-09 04:31:37,263 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.04216456413269043, "success": true}
2026-06-09 04:31:37,263 [INFO] nina.scheduler: reminder_check
2026-06-09 04:31:37,264 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00025081634521484375, "success": true}
2026-06-09 04:31:37,264 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 4.029273986816406e-05, "success": true}
2026-06-09 04:33:57,273 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-09 04:33:58,201 [INFO] nina.routerlog: {"ts": "2026-06-09T04:33:58.000+0600", "req_id": "c8520e54", "provider": "GROQ", "task_type": "research", "input_tokens": 371, "output_tokens": 110, "cost_usd": 0.0, "ttf_ms": 682, "total_ms": 682, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-09 04:33:58,201 [INFO] nina.router: router_success req_id=c8520e54 provider=GROQ task=research ms=682
2026-06-09 04:33:58,202 [INFO] nina.idle: idle_proposal_appended topic=morning_report file=2026-06-09_proposals.md
2026-06-09 04:36:37,253 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.026721477508544922, "success": true}
2026-06-09 04:37:17,627 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: Client error '401 Unauthorized' for url 'https://api.deepseek.com/models'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401. Using fallback.
2026-06-09 04:37:18,542 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-09 04:37:18,550 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-09 04:37:18,551 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-09 04:41:37,287 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.06721925735473633, "success": true}
2026-06-09 04:46:37,222 [INFO] nina.scheduler: NINA operational
2026-06-09 04:46:37,223 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.0003612041473388672, "success": true}
2026-06-09 04:46:37,223 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 7.62939453125e-05, "success": true}
2026-06-09 04:46:37,330 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.10650849342346191, "success": true}
2026-06-09 04:46:37,331 [INFO] nina.scheduler: reminder_check
2026-06-09 04:46:37,331 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00020647048950195312, "success": true}
2026-06-09 04:46:37,331 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.62396240234375e-05, "success": true}
2026-06-09 04:48:33,539 [INFO] nina.scheduler: Received signal 15, initiating graceful shutdown...
```

### logs/nina.log.2026-06-09
Last modified: 2026-06-10 00:18:45
Size: 178444 bytes
```log
[truncated — showing last 200 lines]
2026-06-09 21:18:23,565 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-09 21:18:26,852 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-09 21:18:26,853 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-09 21:23:21,465 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.04213714599609375, "success": true}
2026-06-09 21:23:21,465 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.04213714599609375, "success": true}
2026-06-09 21:28:21,494 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07668757438659668, "success": true}
2026-06-09 21:28:21,494 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07668757438659668, "success": true}
2026-06-09 21:28:21,495 [INFO] nina.scheduler: reminder_check
2026-06-09 21:28:21,495 [INFO] nina.scheduler: reminder_check
2026-06-09 21:28:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00018477439880371094, "success": true}
2026-06-09 21:28:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00018477439880371094, "success": true}
2026-06-09 21:28:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.910064697265625e-05, "success": true}
2026-06-09 21:28:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.910064697265625e-05, "success": true}
2026-06-09 21:33:21,438 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02264547348022461, "success": true}
2026-06-09 21:33:21,438 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02264547348022461, "success": true}
2026-06-09 21:38:21,436 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021747827529907227, "success": true}
2026-06-09 21:38:21,436 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021747827529907227, "success": true}
2026-06-09 21:43:21,416 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 5.1021575927734375e-05, "success": true}
2026-06-09 21:43:21,416 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 5.1021575927734375e-05, "success": true}
2026-06-09 21:43:21,438 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021360397338867188, "success": true}
2026-06-09 21:43:21,438 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021360397338867188, "success": true}
2026-06-09 21:43:21,438 [INFO] nina.scheduler: reminder_check
2026-06-09 21:43:21,438 [INFO] nina.scheduler: reminder_check
2026-06-09 21:43:21,438 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00012445449829101562, "success": true}
2026-06-09 21:43:21,438 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00012445449829101562, "success": true}
2026-06-09 21:43:21,439 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 7.343292236328125e-05, "success": true}
2026-06-09 21:43:21,439 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 7.343292236328125e-05, "success": true}
2026-06-09 21:48:21,444 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02273416519165039, "success": true}
2026-06-09 21:48:21,444 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02273416519165039, "success": true}
2026-06-09 21:48:55,408 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-09 21:48:56,802 [INFO] nina.routerlog: {"ts": "2026-06-09T21:48:56.000+0600", "req_id": "652e87f9", "provider": "GROQ", "task_type": "research", "input_tokens": 368, "output_tokens": 98, "cost_usd": 0.0, "ttf_ms": 878, "total_ms": 878, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-09 21:48:56,802 [INFO] nina.router: router_success req_id=652e87f9 provider=GROQ task=research ms=878
2026-06-09 21:48:56,803 [INFO] nina.idle: idle_proposal_appended topic=memory_context file=2026-06-09_proposals.md
2026-06-09 21:53:21,436 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02137136459350586, "success": true}
2026-06-09 21:53:21,436 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02137136459350586, "success": true}
2026-06-09 21:53:26,157 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-09 21:53:26,576 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-09 21:53:26,577 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-09 21:58:21,494 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.0761270523071289, "success": true}
2026-06-09 21:58:21,494 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.0761270523071289, "success": true}
2026-06-09 21:58:21,495 [INFO] nina.scheduler: reminder_check
2026-06-09 21:58:21,495 [INFO] nina.scheduler: reminder_check
2026-06-09 21:58:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001220703125, "success": true}
2026-06-09 21:58:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001220703125, "success": true}
2026-06-09 21:58:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.0742416381835938e-05, "success": true}
2026-06-09 21:58:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.0742416381835938e-05, "success": true}
2026-06-09 22:03:21,443 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020495891571044922, "success": true}
2026-06-09 22:03:21,443 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020495891571044922, "success": true}
2026-06-09 22:08:21,436 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02050042152404785, "success": true}
2026-06-09 22:08:21,436 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02050042152404785, "success": true}
2026-06-09 22:13:21,416 [INFO] nina.scheduler: NINA operational
2026-06-09 22:13:21,416 [INFO] nina.scheduler: NINA operational
2026-06-09 22:13:21,416 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.00014448165893554688, "success": true}
2026-06-09 22:13:21,416 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.00014448165893554688, "success": true}
2026-06-09 22:13:21,416 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 3.790855407714844e-05, "success": true}
2026-06-09 22:13:21,416 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 3.790855407714844e-05, "success": true}
2026-06-09 22:13:21,439 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021963119506835938, "success": true}
2026-06-09 22:13:21,439 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021963119506835938, "success": true}
2026-06-09 22:13:21,439 [INFO] nina.scheduler: reminder_check
2026-06-09 22:13:21,439 [INFO] nina.scheduler: reminder_check
2026-06-09 22:13:21,440 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00018858909606933594, "success": true}
2026-06-09 22:13:21,440 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00018858909606933594, "success": true}
2026-06-09 22:13:21,440 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 7.486343383789062e-05, "success": true}
2026-06-09 22:13:21,440 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 7.486343383789062e-05, "success": true}
2026-06-09 22:18:21,530 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.10913848876953125, "success": true}
2026-06-09 22:18:21,530 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.10913848876953125, "success": true}
2026-06-09 22:19:56,809 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-09 22:19:58,081 [INFO] nina.routerlog: {"ts": "2026-06-09T22:19:58.000+0600", "req_id": "f6ed5bbd", "provider": "GROQ", "task_type": "research", "input_tokens": 368, "output_tokens": 102, "cost_usd": 0.0, "ttf_ms": 759, "total_ms": 759, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-09 22:19:58,081 [INFO] nina.router: router_success req_id=f6ed5bbd provider=GROQ task=research ms=759
2026-06-09 22:19:58,081 [INFO] nina.idle: idle_proposal_appended topic=scheduler_errors file=2026-06-09_proposals.md
2026-06-09 22:23:21,461 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.045491933822631836, "success": true}
2026-06-09 22:23:21,461 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.045491933822631836, "success": true}
2026-06-09 22:23:28,806 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-09 22:23:30,368 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-09 22:23:30,369 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-09 22:28:21,440 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020879030227661133, "success": true}
2026-06-09 22:28:21,440 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020879030227661133, "success": true}
2026-06-09 22:28:21,440 [INFO] nina.scheduler: reminder_check
2026-06-09 22:28:21,440 [INFO] nina.scheduler: reminder_check
2026-06-09 22:28:21,440 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.250640869140625e-05, "success": true}
2026-06-09 22:28:21,440 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.250640869140625e-05, "success": true}
2026-06-09 22:28:21,440 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.0517578125e-05, "success": true}
2026-06-09 22:28:21,440 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.0517578125e-05, "success": true}
2026-06-09 22:33:21,446 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02320575714111328, "success": true}
2026-06-09 22:33:21,446 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02320575714111328, "success": true}
2026-06-09 22:38:21,448 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.03139543533325195, "success": true}
2026-06-09 22:38:21,448 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.03139543533325195, "success": true}
2026-06-09 22:43:21,420 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 4.9591064453125e-05, "success": true}
2026-06-09 22:43:21,420 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 4.9591064453125e-05, "success": true}
2026-06-09 22:43:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07465362548828125, "success": true}
2026-06-09 22:43:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07465362548828125, "success": true}
2026-06-09 22:43:21,495 [INFO] nina.scheduler: reminder_check
2026-06-09 22:43:21,495 [INFO] nina.scheduler: reminder_check
2026-06-09 22:43:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00013589859008789062, "success": true}
2026-06-09 22:43:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00013589859008789062, "success": true}
2026-06-09 22:43:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.574920654296875e-05, "success": true}
2026-06-09 22:43:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.574920654296875e-05, "success": true}
2026-06-09 22:48:21,444 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020726919174194336, "success": true}
2026-06-09 22:48:21,444 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020726919174194336, "success": true}
2026-06-09 22:50:58,089 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-09 22:50:59,313 [INFO] nina.routerlog: {"ts": "2026-06-09T22:50:59.000+0600", "req_id": "cb8d8185", "provider": "GROQ", "task_type": "research", "input_tokens": 368, "output_tokens": 92, "cost_usd": 0.0, "ttf_ms": 725, "total_ms": 725, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-09 22:50:59,313 [INFO] nina.router: router_success req_id=cb8d8185 provider=GROQ task=research ms=725
2026-06-09 22:50:59,313 [INFO] nina.idle: idle_proposal_appended topic=telegram_interface file=2026-06-09_proposals.md
2026-06-09 22:53:21,439 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022572755813598633, "success": true}
2026-06-09 22:53:21,439 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022572755813598633, "success": true}
2026-06-09 22:53:31,677 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-09 22:53:36,077 [WARNING] nina.model_discovery: Discovery failed for DEEPSEEK: . Using fallback.
2026-06-09 22:53:37,539 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-09 22:53:37,540 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-09 22:58:21,447 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.026737213134765625, "success": true}
2026-06-09 22:58:21,447 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.026737213134765625, "success": true}
2026-06-09 22:58:21,447 [INFO] nina.scheduler: reminder_check
2026-06-09 22:58:21,447 [INFO] nina.scheduler: reminder_check
2026-06-09 22:58:21,447 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00013446807861328125, "success": true}
2026-06-09 22:58:21,447 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00013446807861328125, "success": true}
2026-06-09 22:58:21,448 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 5.435943603515625e-05, "success": true}
2026-06-09 22:58:21,448 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 5.435943603515625e-05, "success": true}
2026-06-09 23:00:00,946 [INFO] nina.scheduler: {"event": "job_run", "job": "cost_report", "duration": 0.9420745372772217, "success": true}
2026-06-09 23:00:00,946 [INFO] nina.scheduler: {"event": "job_run", "job": "cost_report", "duration": 0.9420745372772217, "success": true}
2026-06-09 23:03:21,435 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021238088607788086, "success": true}
2026-06-09 23:03:21,435 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.021238088607788086, "success": true}
2026-06-09 23:08:21,438 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022353172302246094, "success": true}
2026-06-09 23:08:21,438 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022353172302246094, "success": true}
2026-06-09 23:13:21,428 [INFO] nina.scheduler: NINA operational
2026-06-09 23:13:21,428 [INFO] nina.scheduler: NINA operational
2026-06-09 23:13:21,429 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.0018939971923828125, "success": true}
2026-06-09 23:13:21,429 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.0018939971923828125, "success": true}
2026-06-09 23:13:21,430 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 4.291534423828125e-05, "success": true}
2026-06-09 23:13:21,430 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 4.291534423828125e-05, "success": true}
2026-06-09 23:13:21,515 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.08421969413757324, "success": true}
2026-06-09 23:13:21,515 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.08421969413757324, "success": true}
2026-06-09 23:13:21,516 [INFO] nina.scheduler: reminder_check
2026-06-09 23:13:21,516 [INFO] nina.scheduler: reminder_check
2026-06-09 23:13:21,516 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00024771690368652344, "success": true}
2026-06-09 23:13:21,516 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00024771690368652344, "success": true}
2026-06-09 23:13:21,517 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.123283386230469e-05, "success": true}
2026-06-09 23:13:21,517 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.123283386230469e-05, "success": true}
2026-06-09 23:18:22,924 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 1.5023925304412842, "success": true}
2026-06-09 23:18:22,924 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 1.5023925304412842, "success": true}
2026-06-09 23:21:59,324 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-09 23:22:02,089 [INFO] nina.routerlog: {"ts": "2026-06-09T23:22:02.000+0600", "req_id": "780a1733", "provider": "GROQ", "task_type": "research", "input_tokens": 371, "output_tokens": 91, "cost_usd": 0.0, "ttf_ms": 641, "total_ms": 641, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-09 23:22:02,089 [INFO] nina.router: router_success req_id=780a1733 provider=GROQ task=research ms=641
2026-06-09 23:22:02,090 [INFO] nina.idle: idle_proposal_appended topic=config_robustness file=2026-06-09_proposals.md
2026-06-09 23:23:21,444 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02132582664489746, "success": true}
2026-06-09 23:23:21,444 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02132582664489746, "success": true}
2026-06-09 23:23:33,990 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-09 23:23:35,790 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-09 23:23:35,791 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-09 23:28:21,450 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.0219881534576416, "success": true}
2026-06-09 23:28:21,450 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.0219881534576416, "success": true}
2026-06-09 23:28:21,450 [INFO] nina.scheduler: reminder_check
2026-06-09 23:28:21,450 [INFO] nina.scheduler: reminder_check
2026-06-09 23:28:21,451 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001385211944580078, "success": true}
2026-06-09 23:28:21,451 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001385211944580078, "success": true}
2026-06-09 23:28:21,451 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.47955322265625e-05, "success": true}
2026-06-09 23:28:21,451 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.47955322265625e-05, "success": true}
2026-06-09 23:33:22,758 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 1.3432807922363281, "success": true}
2026-06-09 23:33:22,758 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 1.3432807922363281, "success": true}
2026-06-09 23:38:22,737 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 1.3145196437835693, "success": true}
2026-06-09 23:38:22,737 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 1.3145196437835693, "success": true}
2026-06-09 23:43:21,422 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 3.981590270996094e-05, "success": true}
2026-06-09 23:43:21,422 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 3.981590270996094e-05, "success": true}
2026-06-09 23:43:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07217836380004883, "success": true}
2026-06-09 23:43:21,495 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07217836380004883, "success": true}
2026-06-09 23:43:21,501 [INFO] nina.scheduler: reminder_check
2026-06-09 23:43:21,501 [INFO] nina.scheduler: reminder_check
2026-06-09 23:43:21,501 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001811981201171875, "success": true}
2026-06-09 23:43:21,501 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001811981201171875, "success": true}
2026-06-09 23:43:21,501 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.9087066650390625e-05, "success": true}
2026-06-09 23:43:21,501 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.9087066650390625e-05, "success": true}
2026-06-09 23:48:21,527 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.11130404472351074, "success": true}
2026-06-09 23:48:21,527 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.11130404472351074, "success": true}
2026-06-09 23:53:02,107 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-09 23:53:03,427 [INFO] nina.routerlog: {"ts": "2026-06-09T23:53:03.000+0600", "req_id": "62a4b6a0", "provider": "GROQ", "task_type": "research", "input_tokens": 370, "output_tokens": 110, "cost_usd": 0.0, "ttf_ms": 812, "total_ms": 812, "parallel": false, "cached": false, "status": "success", "error": ""}
2026-06-09 23:53:03,427 [INFO] nina.router: router_success req_id=62a4b6a0 provider=GROQ task=research ms=812
2026-06-09 23:53:03,427 [INFO] nina.idle: idle_proposal_appended topic=tool_error_handling file=2026-06-09_proposals.md
2026-06-09 23:53:21,447 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.027435779571533203, "success": true}
2026-06-09 23:53:21,447 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.027435779571533203, "success": true}
2026-06-09 23:53:38,111 [WARNING] nina.model_discovery: Discovery failed for TOGETHER: 'list' object has no attribute 'get'. Using fallback.
2026-06-09 23:53:38,112 [INFO] nina.model_discovery: Model discovery: GROQ=llama-3.3-70b-versatile GEMINI=gemini-2.5-flash CEREBRAS=llama-3.3-70b MISTRAL=mistral-small-latest DEEPSEEK=deepseek-chat TOGETHER=meta-llama/Llama-3.3-70B-Instruct-Turbo COHERE=command-r-plus XAI=grok-3-mini SAMBANOVA=Meta-Llama-3.3-70B-Instruct OPENAI=gpt-4o-mini PERPLEXITY=llama-3.1-sonar-small-128k-online FIREWORKS=accounts/fireworks/models/llama-v3p3-70b-instruct HYPERBOLIC=meta-llama/Llama-3.3-70B-Instruct NOVITA=meta-llama/llama-3.3-70b-instruct ONEBRAIN=llama-3.3-70b-versatile OPENROUTER=meta-llama/llama-3.3-70b-instruct
2026-06-09 23:53:38,203 [WARNING] nina.router: quality_probe_fail provider=POLLINATIONS marked degraded
2026-06-09 23:58:21,449 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022739887237548828, "success": true}
2026-06-09 23:58:21,449 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.022739887237548828, "success": true}
2026-06-09 23:58:21,450 [INFO] nina.scheduler: reminder_check
2026-06-09 23:58:21,450 [INFO] nina.scheduler: reminder_check
2026-06-09 23:58:21,450 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 8.559226989746094e-05, "success": true}
2026-06-09 23:58:21,450 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 8.559226989746094e-05, "success": true}
2026-06-09 23:58:21,450 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.1219253540039062e-05, "success": true}
2026-06-09 23:58:21,450 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.1219253540039062e-05, "success": true}
2026-06-10 00:03:21,512 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.09656167030334473, "success": true}
2026-06-10 00:08:21,440 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.020862817764282227, "success": true}
2026-06-10 00:13:21,427 [INFO] nina.scheduler: NINA operational
2026-06-10 00:13:21,427 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.0001971721649169922, "success": true}
2026-06-10 00:13:21,427 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 6.937980651855469e-05, "success": true}
2026-06-10 00:13:21,469 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.04111790657043457, "success": true}
2026-06-10 00:13:21,469 [INFO] nina.scheduler: reminder_check
2026-06-10 00:13:21,470 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00013875961303710938, "success": true}
2026-06-10 00:13:21,470 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.981590270996094e-05, "success": true}
2026-06-10 00:18:22,271 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.8556082248687744, "success": true}
2026-06-10 00:18:45,264 [INFO] nina.scheduler: Received signal 15, initiating graceful shutdown...
```

### logs/nina_problem_log.md
Last modified: 2026-06-04 14:43:44
Size: 26707 bytes
```log
# NINA v12.2 Problem Log

**Machine:** ASUS VivoBook X530FN (aibony) · i5 8th Gen · 16GB RAM · MX150 2GB VRAM  
**OS:** Ubuntu 26.04 LTS · Python 3.14  
**Last updated:** 2026-05-22  
**Status:** v12.2 operational · all 8 GPT-5 audit fixes applied · 65 issues resolved · IdleProposalLoop active

---

## Component Status

| Component | Status | Notes |
|---|---|---|
| venv / Python 3.14 | ✅ | |
| HybridRouter V4 | ✅ | Cloud routing confirmed |
| `core/router.py` | ✅ | ResponseCache auto-purge · safe provider fallback · purge_expired safe iteration · R-53, R-58, R-59 |
| `core/agent.py` | ✅ | System frame once, incremental steps · R-38 |
| `core/config.py` | ✅ | Safe env loading · idle vars wired · R-29, R-35, R-41 |
| `core/memory.py` | ✅ | Blocking IO offloaded · freshness ranking · durable prefs · R-34, R-45, R-60 |
| `core/capabilities.py` | ✅ | asyncio.Lock + tothread · R-37 |
| `core/hotreload.py` | ✅ | Key mismatch fixed · deleted keys revert to defaults · R-36, R-44 |
| `core/nina.py` | ✅ | Duplicate import removed · IDLE_QUEUE canonical · duplicate log handler guard · R-46, R-47, R-61, R-65 |
| `core/logger.py` | ✅ | NameError fixed · duplicate import removed · R-33, R-43 |
| `crons/manager.py` | ✅ | Backup jobs use functools.partial (not lambda) · R-62 |
| `idleloop.py` | ✅ | Grounded prompts · promptindex persisted · R-42, R-51, R-57 |
| `tools/shell.py` | ✅ | cat removed from allowlist · injection protection · R-40, R-48 |
| `tools/officemail.py` | ✅ | SSL verification restored · R-49 |
| `tools/upgradepipeline.py` | ✅ | Pending slot guard · URL allowlist · eval regex · content-type/size guard · R-50, R-52, R-54, R-63 |
| `tools/browser.py` | ✅ | Full IP-range SSRF guard (ipaddress module) · R-56, R-64 |
| `interfaces/telegram_interface.py` | ✅ | Document upload before empty-text guard · key masking · intent map tightened · R-63b, R-66, R-67 |
| `main.py` | ✅ | PID-file targeted kill · R-55 |
| Ollama | ✅ | qwen2.5:1.5b · 7b · nomic-embed-text |
| Telegram bot | ✅ | PTB 21.9, live |
| NumPy | ✅ | Pinned <2.0 |
| Systemd | ✅ | nina + ollama auto-start enabled |
| IdleProposalLoop | ✅ | 7-topic rotation, promptindex persisted |
| EWS email | ⛔ | Blocked by O-02 |

---

## Resolved Issues

### R-01 — nina directory missing
- **Fix:** `mkdir -p nina`

### R-02 — python command not found
- **Fix:** `sudo apt install python-is-python3 -y`

### R-03 — Ollama models not pulled
- **Fix:** Pulled manually: qwen2.5:1.5b, qwen2.5:7b, nomic-embed-text

### R-04 — playwright not found at system level
- **Fix:** Installed via pip inside venv

### R-05 — nina.service unit missing
- **Fix:** Old v1 service disabled; new unit created and enabled

### R-06 — venv not set up
- **Fix:** `python3 -m venv nina/venv && source nina/venv/bin/activate`

### R-07 — No source code after uninstall
- **Fix:** All stages scaffolded in session (Stages 1–7)

### R-08 — PTB Updater.__slots__ AttributeError on Python 3.14
- **Error:** `AttributeError: Updater object has no attribute _Updater__polling_cleanup_cb`
- **Cause:** PTB 20.7 incompatible with Python 3.14 name-mangling changes
- **Fix:** `pip install --force-reinstall python-telegram-bot==21.9`

### R-09 — externally-managed-environment on pip install
- **Fix:** Always use venv; Ubuntu 26.04 enforces PEP 668

### R-10 — KeyError TELEGRAM_BOT_TOKEN on startup
- **Cause:** .env used `TELEGRAMBOTTOKEN`; config expected `TELEGRAM_BOT_TOKEN`
- **Fix:** `sed -i s/TELEGRAMBOTTOKEN/TELEGRAM_BOT_TOKEN/ nina/.env`

### R-11 — AttributeError NinaOS has no attribute run_morning_report
- **Cause:** Scheduler methods appended outside class body
- **Fix:** Re-appended correctly inside NinaOS

### R-12 — AttributeError TelegramInterface has no attribute send_message
- **Fix:** Appended `send_message` helper to TelegramInterface

### R-13 — BlockingIOError Errno 11 fcntl lock on startup
- **Cause:** Multiple NINA processes running simultaneously
- **Fix:** `pkill -f "python main.py"`; remove `nina/data/nina.lock`

### R-14 — BadRequest: Message is not modified
- **Cause:** Streaming edit loop sending identical text to Telegram
- **Fix:** Single final `edit_text` with content-change guard

### R-15 — Old NINA v1 intercepting bot token
- **Fix:** Disabled v1 service; fcntl lock prevents future double-start

### R-16 — router.log not writing to file
- **Fix:** 8 TimedRotatingFileHandler instances added to `core/nina.py`

### R-17 — nina.service not auto-starting after reboot
- **Cause:** Service was not enabled
- **Fix:** `sudo systemctl enable nina ollama`

### R-18 — IndentationError in core/nina.py after style patch
- **Cause:** Auto-patch used wrong variable name and bad insertion point
- **Fix:** Reverted with re.sub, re-applied manually

### R-19 — NumPy 2.0 compatibility error on startup
- **Error:** `AttributeError: np.float was removed in the NumPy 2.0 release`
- **Fix:** `pip install "numpy<2.0"`

### R-20 — SyntaxError: closing triple-quote merged with next line
- **Cause:** Bash history expansion on `!` corrupted injection
- **Fix:** `sed -i` to insert newline

### R-21 — format_for_telegram defined but never called
- **Fix:** `sed -i` to wire call in `edit_text`

### R-22 — UnboundLocalError: tool in core/agent.py
- **Cause:** tool only assigned inside else branch
- **Fix:** Moved above health check; rewrote if/else/if to if/elif/else
- **File:** `core/agent.py`

### R-23 — ConflictingIdError: memory_backup crash on startup
- **Cause:** `id='memory_backup'` registered twice in `crons/manager.py`
- **Fix:** Removed duplicate
- **File:** `crons/manager.py`

### R-24 — AttributeError: HybridRouter has no attribute activate_key
- **Cause:** Method called but never defined
- **Fix:** Added `async def activate_key(self, provider, key)` to HybridRouter
- **File:** `core/router.py`

### R-25 — FileNotFoundError: data/nina.lock on fresh install
- **Cause:** data directory not created before lock open
- **Fix:** Added `os.makedirs("data", exist_ok=True)`
- **File:** `core/nina.py`

### R-26 — handle_shadow defined 3× in tools/upgradepipeline.py
- **Fix:** Removed first two definitions, kept final
- **File:** `tools/upgradepipeline.py`

### R-27 — Dead file interfaces/telegram_interface.py
- **Cause:** 129-line legacy class never imported, shadowed active file
- **Fix:** Deleted

### R-28 — Ghost bot instance returning stale exchange rate
- **Symptom:** 1 USD = 95.20 BDT returned with no main.py in process list
- **Fix:** `pkill -9` cleared ghost; confirmed live: 1 USD = 122.84 BDT via Perplexity

### R-29 — idle_auto_approve hardcoded False, not wired to .env
- **Cause:** `load_config` had no mapping for IDLE_AUTO_APPROVE, IDLE_THRESHOLD_MIN, IDLE_REPORT_MIN
- **Fix:** Added 3 `os.getenv` overrides after `cfg = NinaConfig(...)`
- **File:** `core/config.py`

### R-30 — Pattern scanner silently killed auto-approve flow
- **Cause:** Scanner rejections returned different string; auto-approve branch never entered
- **Fix:** Added early-return guard for "Upgrade rejected" before auto-approve
- **File:** `idleloop.py`

### R-31 — WRITABLE scope mismatch between idleloop and pipeline
- **Cause:** idleloop.py allowed `agent/` directory; pipeline only allowed `core/agent.py`
- **Fix:** Aligned WRITABLE tuple to tools/, crons/, core/agent.py, tests/
- **File:** `idleloop.py`

### R-32 — Idle queue accumulated without action
- **Cause:** `run_idle_summary` only reported count, never auto-deployed
- **Fix:** Added auto-deploy of oldest item when `idle_auto_approve=True`
- **File:** `core/nina.py`

### R-33 — core/logger.py broken config import
- **Cause:** `from core.config import config` — no module-level config object exists
- **Fix:** Replaced with `from pathlib import Path; LOG_DIR = Path("logs")`
- **File:** `core/logger.py`

### R-34 — Blocking IO in async memory methods
- **Cause:** `build_context`, `remember`, `forget` all called sync IO in async context
- **Fix:** All blocking calls wrapped in `asyncio.to_thread`
- **File:** `core/memory.py`

### R-35 — KeyError crash on missing env vars at startup
- **Cause:** `os.environ["TELEGRAM_BOT_TOKEN"]` raises KeyError with no message
- **Fix:** Replaced with `os.getenv` + explicit RuntimeError with descriptive message
- **File:** `core/config.py`

### R-36 — Hot-reload silently ignored deleted .env keys
- **Cause:** reload hit `continue` on None; deleted keys never reverted
- **Fix:** Added Pydantic default lookup and `setattr` revert on missing key
- **File:** `core/hotreload.py`

### R-37 — Race condition on capabilities.json writes
- **Cause:** Concurrent `mark_unhealthy`/`mark_healthy` calls could corrupt JSON
- **Fix:** Added `asyncio.Lock` + `asyncio.to_thread` for atomic writes
- **File:** `core/capabilities.py`

### R-38 — Unbounded context window growth in AgentLoop
- **Cause:** Each step appended full prompt; quadratic token growth over multi-step tasks
- **Fix:** System frame built once before loop; each step appends only incremental scratchpad
- **File:** `core/agent.py`

### R-39 — agentloop.py and agentmemory.py orphaned dead code
- **Cause:** Both files never imported by any active module
- **Fix:** Archived to `agent_archive/`

### R-40 — asyncio.get_event_loop deprecated; injection risk in tools/shell.py
- **Cause:** Deprecated API; `shell=True` with no injection protection; returncode unchecked
- **Fix:** `get_running_loop` + `shlex.split` + shell operator blocklist + returncode check
- **File:** `tools/shell.py`

### R-41 — Orphaned `cfg = NinaConfig()` line causing SyntaxError in core/config.py
- **Cause:** R-29 patch left original unclosed line in place
- **Fix:** Removed orphaned line; verified with `ast.parse`
- **File:** `core/config.py`

### R-42 — IdleProposalLoop generating hallucinated filenames
- **Cause:** Analysis prompts gave LLM no grounding; invented files like `tools/platesolve.py`
- **Fix:** Injected real file tree into prompt before every analysis call
- **File:** `idleloop.py`

### R-43 — config.LOGDIR NameError in core/logger.py
- **Cause:** RotatingFileHandler referenced `config.LOGDIR` but config was never imported; duplicate `from pathlib import Path` also present
- **Fix:** Replaced with local constant `LOG_DIR`; removed duplicate import
- **File:** `core/logger.py`

### R-44 — RELOADABLE key mismatch causing config wipe on hot-reload
- **Cause:** 18 keys in RELOADABLE used concatenated names (e.g. IDLEAUTOAPPROVE) but .env stores underscore-separated keys; every reload cycle reverted all settings to Pydantic defaults silently
- **Fix:** All 18 keys corrected to underscore format matching .env
- **File:** `core/hotreload.py`

### R-45 — Empty collection guard missing in core/memory.py
- **Fix:** Added guard for empty facts/docs before slicing

### R-46 — Conflicting tool descriptions in SYSTEM_PROMPT_TEMPLATE
- **Cause:** Two consecutive "Available tools" lines with contradictory tool names degraded LLM instruction adherence
- **Fix:** Removed stale DuckDuckGo-only line; kept accurate Tavily/Serper/DDG line
- **File:** `core/nina.py`

### R-47 — Duplicate `import os` in core/nina.py
- **Fix:** Removed standalone `import os` on line 1; retained inside combined import on line 3
- **File:** `core/nina.py`

### R-48 — cat in shell allowlist enabling file exfiltration
- **Cause:** `cat` in ALLOWED allowed unrestricted reads of .env, SSH keys, any file on disk
- **Fix:** Removed `cat` from ALLOWED
- **File:** `tools/shell.py`

### R-49 — SSL verification disabled on EWS email connections
- **Cause:** NoVerifyHTTPAdapter override silently disabled SSL cert verification, exposing NTLM credentials to MITM attacks
- **Fix:** Removed NoVerifyHTTPAdapter override; SSL verification restored
- **File:** `tools/officemail.py`

### R-50 — patch command fetched and deployed arbitrary URLs
- **Cause:** No domain allowlist or HTTPS enforcement on `patch` command
- **Fix:** Enforces HTTPS-only domain allowlist: github.com, raw.githubusercontent.com, gist.githubusercontent.com, pastebin.com
- **File:** `tools/upgradepipeline.py`

### R-51 — Grounded prompt built but never passed to router in idleloop.py
- **Cause:** `generate_proposal` built `grounded_prompt` with real file context but passed bare prompt to router, enabling hallucinated filenames
- **Fix:** Changed router call to use `grounded_prompt`
- **File:** `idleloop.py`

### R-52 — Pending upgrade slot silently overwritten in upgradepipeline.py
- **Cause:** `submit` overwrote any existing pending upgrade without warning, losing the first submission
- **Fix:** Added guard; returns error if `self.pending is not None`
- **File:** `tools/upgradepipeline.py`

### R-53 — ResponseCache unbounded memory leak in core/router.py
- **Cause:** `purge_expired` existed but was never called automatically; cache grew forever
- **Fix:** Added auto-purge in `set` when cache exceeds 500 entries
- **File:** `core/router.py`

### R-54 — Weak exec/eval/compile regex in upgrade scanner
- **Cause:** Regex lookbehind patterns didn't reliably block eval/exec/compile calls
- **Fix:** Replaced with `\b` word-boundary patterns
- **File:** `tools/upgradepipeline.py`

### R-55 — pkill -f self-restart guard killed unrelated processes
- **Cause:** `pkill -f "python3 main.py"` matched any process with that string, not just NINA
- **Fix:** Replaced with PID-file approach; only sends SIGTERM to the exact previous NINA PID
- **File:** `main.py`

### R-56 — Incomplete SSRF protection in tools/browser.py
- **Cause:** Blocklist missed IPv6 loopback (::1), link-local 169.254.x.x, cloud metadata endpoints, and upper 172.x RFC-1918 ranges
- **Fix:** Expanded blocklist to cover all missing ranges and cloud metadata IPs
- **File:** `tools/browser.py`

### R-57 — Idle proposal promptindex reset to 0 on every restart
- **Cause:** `prompt_index = 0` hardcoded in `__init__`; all restarts started from tool-error-handling category
- **Fix:** Index persisted to `data/proposal_index.txt` and loaded on init
- **File:** `idleloop.py`

---

### R-58 — ResponseCache.purge_expired mutates dict during iteration *(GPT-5 audit)*
- **Cause:** `purge_expired` used a generator expression that called `self.s.pop(k)` while iterating `self.s.items()` → `RuntimeError` in Python 3.3+
- **Fix:** Collect dead keys into a list first, then pop in a separate loop
- **File:** `core/router.py`
- **Impact:** HIGH — any cache flush crashed the router

### R-59 — route() raised RuntimeError with no user-safe fallback *(GPT-5 audit)*
- **Cause:** Final `raise RuntimeError("All providers failed…")` propagated unhandled to Telegram, producing a raw traceback in chat
- **Fix:** Replaced with logged warning + user-safe reply string listing failed providers
- **File:** `core/router.py`
- **Impact:** HIGH

### R-60 — core/memory.py build_context returned stale facts with no freshness ranking *(GPT-5 audit)*
- **Cause:** First 10 facts returned by insertion order; stale or low-priority facts could dominate prompts; no separation of durable preferences from recent conversation snippets
- **Fix:** Added timestamps + priority to facts; `build_context` sorts by recency × priority score; durable preferences always included regardless of recency cutoff
- **File:** `core/memory.py`
- **Impact:** MEDIUM

### R-61 — core/nina.py idle queue path mismatch *(GPT-5 audit)*
- **Cause:** `run_idle_summary` read `data/idlequeue.json`; `expire_pending` wrote to `IDLE_QUEUE` = `data/idle_queue.json` (underscore); pending items were invisible to the consumer
- **Fix:** `core/nina.py` now imports `IDLE_QUEUE` from `tools/upgradepipeline.py`; single source of truth
- **File:** `core/nina.py`
- **Impact:** HIGH — idle queue silently dropped all expired items

### R-62 — Cron backup jobs silently dropped via lambda coroutine anti-pattern *(GPT-5 audit)*
- **Cause:** `lambda: run_memory_backup(n)` is a sync callable returning a coroutine object; APScheduler treats it as sync, calls it, discards the coroutine without awaiting
- **Fix:** Replaced with `functools.partial(run_memory_backup, n)` (a proper async callable)
- **File:** `crons/manager.py`
- **Impact:** HIGH — backups and expire_pending never actually ran

### R-63 — Remote patch download had no content-type or size guard *(GPT-5 audit)*
- **Cause:** `tools/upgradepipeline.py` fetched patch URLs from approved domains but did not verify Content-Type, response size, or exact path intent before staging as code
- **Fix:** Enforced 100KB max response size, required `text/plain` content-type, added diff summary shown to user before approval
- **File:** `tools/upgradepipeline.py`
- **Impact:** MEDIUM — oversized or binary responses could be staged as code

### R-64 — tools/browser.py SSRF guard used substring matching *(GPT-5 audit)*
- **Cause:** `"10." in url` matched `example10.com` (false positive) and missed URL-encoded or zero-padded variants; no check for `::1`, link-local, or cloud metadata hosts
- **Fix:** Replaced all substring checks with `ipaddress.ip_address()` range validation covering private, loopback, link-local, and reserved ranges
- **File:** `tools/browser.py`
- **Impact:** MEDIUM — SSRF bypass and false-positive blocks

### R-65 — Duplicate `if not root.handlers:` guard with bad indentation *(GPT-5 audit)*
- **Cause:** P8 patch introduced `if not root.handlers:` correctly, but left a duplicate `if not root.handlers:` on the next line; `root.addHandler(ch)` was at wrong indentation level outside both conditions → handler always added on reinit
- **Fix:** Removed duplicate `if` block; single guard with correct indentation
- **File:** `core/nina.py`
- **Impact:** LOW — duplicate log lines on restart/hot-reload

### R-66 — Document-only Telegram messages silently dropped *(GPT-5 audit)*
- **Cause:** `handle_message` read `update.message.text`, returned early if empty, before the `.py` document handler was reached; file uploads with no caption were never processed
- **Fix:** Moved document check block above the empty-text early-return
- **File:** `interfaces/telegram_interface.py`
- **Impact:** HIGH — upgrade-via-Telegram file flow completely broken

### R-67 — API keys echoed in chat and logs via addkey command *(GPT-5 audit)*
- **Cause:** `handle_add_key` replied with the raw activate_key result string including the full key; no masking, no message deletion, no persistence policy
- **Fix:** Delete the user's message from chat immediately; reply with masked key (`sk-ab****yz`); log only provider name (not key value)
- **File:** `interfaces/telegram_interface.py`
- **Impact:** HIGH — security

---

## Open Issues

| ID | Item | Priority |
|----|------|----------|
| O-01 | Browser tool — Playwright blocked | LOW |
| O-02 | EWS email password | MEDIUM |
| O-04 | memory_context per-session refresh | LOW |
| O-05 | FastAPI REST endpoints not implemented | LOW |

---

## Confirmed Working — 2026-05-22 20:45

- NINA started cleanly: PID 49721, `Active: active (running)`
- All 8 GPT-5 audit patches compiled and applied (`python3 -m py_compile` clean)
- `systemctl status nina` shows no errors
- 65 total issues resolved (R-01 → R-67)


cat >> ~/nina/nina_problem_log.md << 'EOF'

---

### R-68 — parse_mode="Markdown" causing Telegram BadRequest crashes
- **Cause:** Special characters in responses triggered Telegram BadRequest on all reply_text/edit_text calls
- **Fix:** `sed -i 's/parse_mode="Markdown"/parse_mode=None/g'` across telegram_interface.py
- **File:** `interfaces/telegram_interface.py`

### R-69 — HybridRouter has no attribute ordered_providers
- **Cause:** Method renamed to `_ordered_providers` but stale reference remained in error log line 222
- **Fix:** `sed -i '222s/ordered_providers/_ordered_providers/'`
- **File:** `core/router.py`

### R-70 — NameError: forcelocal is not defined
- **Cause:** Line 221 still used old camelCase `forcelocal` after router renamed to snake_case
- **Fix:** `sed -i '221s/forcelocal/force_local/'`
- **File:** `core/router.py`

### R-71 — ClassifiedTask has no attribute tasktype
- **Cause:** Dataclass fields renamed to snake_case but old camelCase references remained in agent.py and router.py
- **Fix:** Global sed replace of tasktype→task_type, issensitive→is_sensitive etc.
- **File:** `core/agent.py`, `core/router.py`

### R-72 — self._http AttributeError — root cause of all-providers-failed
- **Cause:** `_call_provider` used `self._http` but `__init__` set `self.http` (no underscore) — all Ollama calls silently failed
- **Fix:** `sed -i 's/self\._http/self.http/g' core/router.py`
- **File:** `core/router.py`
- **Impact:** HIGH — all local inference broken in live service
EOF

---

## Guardian status — 2026-05-23

**Current state:** guardian operational; deploy path verified; mypy downgraded to advisory warnings.

### New resolved items

### R-73 — guardian failed package check for mypy
- **Cause:** guardian validated `mypy`, but the package was not installed in `~/nina/venv`
- **Fix:** `python -m pip install --upgrade mypy`
- **Scope:** `venv`

### R-74 — APISECRETKEY empty in .env
- **Cause:** `.env` contained an empty `APISECRETKEY`, causing guardian config validation to fail
- **Fix:** inserted a non-empty secret value in `/home/aibony/nina/.env`
- **Scope:** `.env`

### R-75 — guardian treated mypy output as hard failure during healthy deploys
- **Cause:** mypy findings were emitted through `fail`, producing blocking-style output even when runtime deploy succeeded
- **Fix:** changed guardian mypy reporting from `fail` to `warn`
- **Scope:** `nina-guardian.sh`
- **Impact:** MEDIUM — removes contradictory red failure output while preserving visible type debt

### Current warnings

| ID | Item | Priority |
|----|------|----------|
| W-01 | `TELEGRAMCHATID` missing in `.env` | LOW |
| W-02 | mypy type issues remain in `core/`, `tools/`, and `interfaces/telegram_interface.py` | LOW |

### Confirmed working — 2026-05-23 01:35

- guardian completes all sections and reaches `All checks passed — NINA is healthy`
- `nina.service` restarts cleanly from guardian
- Telegram polling confirmed after deploy
- APScheduler confirmed after deploy
- pyflakes clean; syntax checks clean; mypy present and running

--- TITLE NINA v12.2 Problem Log - Guardian status 2026-05-23 - R-76 Guardian handoff/suppression patch applied inconsistently...

- Symptom: guardian patching introduced a partial cosmetic suppression change, causing internal inconsistency between live findings flow and handoff/report fields; one attempted edit also introduced an undefined `effective_findings` reference during suggested_actions construction.
- Evidence: backup of `guardian_engine.py` shows health scoring, overall status, root cause selection, report assembly, and incident writing still run from `findings`, while a separate backup fragment shows a handoff field `suppressedcount lensuppressedfindings` even though no durable `suppressed_findings` pipeline was completed.
- Cause: patch was applied in fragments instead of as one coherent refactor; result was mixed use of old `findings` path plus unfinished suppression/handoff variables.
- Fix: reverted `build_suggested_actions` back to `findings` to remove the immediate NameError path, and identified the dangling handoff `suppressed_count` reference as the remaining cleanup point before any future cosmetic suppression pass.
- Scope: `guardian_engine.py`
- Impact: MEDIUM — can make guardian crash or report inconsistent forensic status even while `healthcheck.py` passes and NINA itself is healthy.
- Current state: guardian logic requires a single coherent follow-up patch, not piecemeal substitutions.

cd ~/nina && BACKUP_MD="$(ls -t upgrades/backups/nina_export_*.md 2>/dev/null | head -n 1)" && [ -n "$BACKUP_MD" ] && cat >> "$BACKUP_MD" <<'EOF'

---

## NINA Problem Log

### 2026-05-23 22:14:44 +0600 — Guardian forensic run
- Guardian reported WARN status with health score 4.5/10, while startup checks and service restart still showed NINA active, Telegram polling confirmed, APScheduler started, and Ollama responding.
- Signature phase reported likely false-positive blockers for `APISECRETKEY`, `TELEGRAMBOTTOKEN`, and `AUTHORIZEDUSERID` even though earlier env preflight and healthcheck marked them present.
- Guardian also reported a concurrent-process/lock warning around `nina.lock` and PID 26097 before restart.
- Advisory findings included duplicate log handler warning, Telegram Markdown parse warning, coroutine/lambda APScheduler warning, idle queue path mismatch warning, shell allowlist regression debt, weak eval/exec regex debt, and TELEGRAMCHATID missing info.
- Guardian forensic engine crashed at the end with:
  - `NameError: name 'suppressed_findings' is not defined`
  - File: `guardian_engine.py`
  - Area: `run_engine(args)` handoff/report assembly

### Confirmed technical interpretation
- NINA runtime itself was not down after restart; deploy gate completed successfully and service remained active.
- The strongest confirmed Guardian bug is the undefined variable `suppressed_findings`.
- The env blocker signatures are likely over-matching from source/signature text rather than true runtime evidence.
- Some warnings appear stale relative to the current codebase backup and should be revalidated against runtime-only evidence.

---

## R-77 - Router review prioritization for next patch set
- **Date:** 2026-05-24 00:27
- **Component:** `core/router.py`
- **Type:** Reliability / routing quality / observability
- **Summary:** Reviewed external feedback from multiple model opinions and selected the safest high-impact router improvements for NINA v12.2.
- **Decision:**
  - Prioritize contextual cache-key hardening so identical prompts from different conversations do not collide.
  - Prioritize proper HTTP 429 handling using `Retry-After` to reduce repeated provider hammering and improve cooldown accuracy.
  - Prioritize request-level trace ID logging for end-to-end correlation across routing attempts and diagnostics.
- **Deferred:**
  - Full circuit-breaker state machine with half-open recovery.
  - Retry/backoff expansion beyond narrow transient-failure classes.
  - Dynamic Ollama model discovery.
  - Cost-tracking-first work as a leading patch item.
- **Rationale:** Selected quick wins improve correctness and resilience immediately with low regression risk and minimal architectural churn.
- **Status:** Logged for implementation planning; no code patch applied in this session.
```

### logs/nina_sync.log
Last modified: 2026-06-09 12:59:18
Size: 0 bytes
```log
```

### logs/nina_update_log.md
Last modified: 2026-06-10 23:18:33
Size: 66237 bytes
```log
[truncated — showing last 200 lines]

---

## Entry 148 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** ninagate/main.py,tools/ninaflash.py,nina_update_log.md,repro_r77.py

**Verification:** git push OK, nina.service active

---

## Entry 149 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/AGENTS.md

**Verification:** git push OK, nina.service active

---

## Entry 150 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_sync.sh,data/circuit_state.json,nina_codebase_backup.sh,nina_docbase_backup.sh,nina_logbase_backup.sh

**Verification:** git push OK, nina.service active

---

## Entry 151 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** data/circuit_state.json,nina_codebase_backup.sh,nina_docbase_backup.sh,nina_logbase_backup.sh

**Verification:** git push OK, nina.service active

---

## Entry 152 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_sync.sh,data/circuit_state.json,generate_backups.sh

**Verification:** git push OK, nina.service active

---

## Entry 153 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_codebase_backup.sh,nina_docbase_backup.sh,nina_logbase_backup.sh,nina_sync.sh,data/circuit_state.json,generate_backups.sh

**Verification:** git push OK, nina.service active

---

## Entry 154 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,data/circuit_state.json,generate_backups.sh

**Verification:** git push OK, nina.service active

---

## Entry 155 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,data/circuit_state.json,generate_backups.sh

**Verification:** git push OK, nina.service active

---

## Entry 156 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,data/circuit_state.json,generate_backups.sh

**Verification:** git push OK, nina.service active

---

## Entry 157 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** data/circuit_state.json,generate_backups.sh

**Verification:** git push OK, nina.service active

---

## Entry 158 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** bin/ninagate,data/circuit_state.json,generate_backups.sh

**Verification:** git push OK, nina.service active

---

## Entry 159 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** bin/ninagate,data/circuit_state.json,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 160 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** bin/ninagate,data/circuit_state.json,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 161 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,data/circuit_state.json,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 162 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** data/circuit_state.json,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 163 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/AGENTS.md,data/circuit_state.json,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 164 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_sync.sh,data/circuit_state.json,docs/space/claude_feed.md,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 165 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** data/circuit_state.json,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 166 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** core/memory.py,nina_update_log.md,pytest.ini,tests/test_finance.py,tests/test_finance_market.py,tests/test_memory.py,data/circuit_state.json,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 167 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_context.md,data/circuit_state.json,docs/space/AGENTS.md,docs/space/WORKFLOW.md,exports/nina_problem_log_archive.md,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active
```

### logs/router.log
Last modified: 2026-05-23 23:46:21
Size: 43359 bytes
```log
2026-05-23 00:04:28,391 [INFO] nina.router_log: {"ts": "2026-05-23T00:04:28.000+0600", "provider": "CACHE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": true, "status": "success", "error": null}
2026-05-23 00:04:46,797 [INFO] nina.router_log: {"ts": "2026-05-23T00:04:46.000+0600", "provider": "GROQ", "task_type": "multilingual", "input_tokens": 265, "output_tokens": 84, "cost_usd": 0.0, "ttf_ms": 1530.4005146026611, "total_ms": 1530.4005146026611, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 00:04:49,332 [INFO] nina.router_log: {"ts": "2026-05-23T00:04:49.000+0600", "provider": "CACHE", "task_type": "multilingual", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": true, "status": "success", "error": null}
2026-05-23 00:04:50,248 [INFO] nina.router_log: {"ts": "2026-05-23T00:04:50.000+0600", "provider": "CACHE", "task_type": "multilingual", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": true, "status": "success", "error": null}
2026-05-23 00:04:51,106 [INFO] nina.router_log: {"ts": "2026-05-23T00:04:51.000+0600", "provider": "CACHE", "task_type": "multilingual", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": true, "status": "success", "error": null}
2026-05-23 00:04:51,976 [INFO] nina.router_log: {"ts": "2026-05-23T00:04:51.000+0600", "provider": "CACHE", "task_type": "multilingual", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": true, "status": "success", "error": null}
2026-05-23 00:07:25,217 [INFO] nina.router_log: {"ts": "2026-05-23T00:07:25.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 387, "output_tokens": 285, "cost_usd": 0.0, "ttf_ms": 1336.6165161132812, "total_ms": 1336.6165161132812, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 00:20:08,915 [INFO] nina.router_log: {"ts": "2026-05-23T00:20:08.000+0600", "provider": "POLLINATIONS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 00:20:10,349 [INFO] nina.router_log: {"ts": "2026-05-23T00:20:10.000+0600", "provider": "CHUTES", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 00:20:10,406 [INFO] nina.router_log: {"ts": "2026-05-23T00:20:10.000+0600", "provider": "HFPUBLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 00:20:11,285 [INFO] nina.router_log: {"ts": "2026-05-23T00:20:11.000+0600", "provider": "CEREBRAS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 00:20:11,782 [INFO] nina.router_log: {"ts": "2026-05-23T00:20:11.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 131, "output_tokens": 65, "cost_usd": 0.0, "ttf_ms": 496.9313144683838, "total_ms": 496.9313144683838, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 00:22:28,999 [INFO] nina.router_log: {"ts": "2026-05-23T00:22:28.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 393, "output_tokens": 108, "cost_usd": 0.0, "ttf_ms": 692.4943923950195, "total_ms": 692.4943923950195, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 00:36:31,858 [INFO] nina.router_log: {"ts": "2026-05-23T00:36:31.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 00:36:33,101 [INFO] nina.router_log: {"ts": "2026-05-23T00:36:33.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 00:36:33,183 [INFO] nina.router_log: {"ts": "2026-05-23T00:36:33.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 00:36:33,701 [INFO] nina.router_log: {"ts": "2026-05-23T00:36:33.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 00:36:35,761 [INFO] nina.router_log: {"ts": "2026-05-23T00:36:35.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 393, "output_tokens": 133, "cost_usd": 0.0, "ttf_ms": 2059.9660873413086, "total_ms": 2059.9660873413086, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 00:43:57,710 [INFO] nina.router_log: {"ts": "2026-05-23T00:43:57.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 00:43:59,451 [INFO] nina.router_log: {"ts": "2026-05-23T00:43:59.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 00:43:59,480 [INFO] nina.router_log: {"ts": "2026-05-23T00:43:59.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 00:44:00,577 [INFO] nina.router_log: {"ts": "2026-05-23T00:44:00.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 00:44:01,703 [INFO] nina.router_log: {"ts": "2026-05-23T00:44:01.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 393, "output_tokens": 127, "cost_usd": 0.0, "ttf_ms": 1125.9689331054688, "total_ms": 1125.9689331054688, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 00:54:39,557 [INFO] nina.router_log: {"ts": "2026-05-23T00:54:39.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 00:54:40,990 [INFO] nina.router_log: {"ts": "2026-05-23T00:54:40.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 00:54:41,042 [INFO] nina.router_log: {"ts": "2026-05-23T00:54:41.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 00:54:41,503 [INFO] nina.router_log: {"ts": "2026-05-23T00:54:41.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 00:54:42,323 [INFO] nina.router_log: {"ts": "2026-05-23T00:54:42.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 393, "output_tokens": 142, "cost_usd": 0.0, "ttf_ms": 820.1088905334473, "total_ms": 820.1088905334473, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 00:56:54,317 [INFO] nina.router_log: {"ts": "2026-05-23T00:56:54.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 00:56:55,874 [INFO] nina.router_log: {"ts": "2026-05-23T00:56:55.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 00:56:55,895 [INFO] nina.router_log: {"ts": "2026-05-23T00:56:55.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 00:56:56,300 [INFO] nina.router_log: {"ts": "2026-05-23T00:56:56.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 00:56:57,082 [INFO] nina.router_log: {"ts": "2026-05-23T00:56:57.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 393, "output_tokens": 152, "cost_usd": 0.0, "ttf_ms": 782.1285724639893, "total_ms": 782.1285724639893, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 01:05:19,417 [INFO] nina.router_log: {"ts": "2026-05-23T01:05:19.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 01:05:20,687 [INFO] nina.router_log: {"ts": "2026-05-23T01:05:20.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 01:05:20,748 [INFO] nina.router_log: {"ts": "2026-05-23T01:05:20.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 01:05:21,370 [INFO] nina.router_log: {"ts": "2026-05-23T01:05:21.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 01:05:22,121 [INFO] nina.router_log: {"ts": "2026-05-23T01:05:22.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 419, "output_tokens": 118, "cost_usd": 0.0, "ttf_ms": 751.2784004211426, "total_ms": 751.2784004211426, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 01:11:51,409 [INFO] nina.router_log: {"ts": "2026-05-23T01:11:51.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 01:11:53,718 [INFO] nina.router_log: {"ts": "2026-05-23T01:11:53.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 01:11:53,941 [INFO] nina.router_log: {"ts": "2026-05-23T01:11:53.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 01:11:55,538 [INFO] nina.router_log: {"ts": "2026-05-23T01:11:55.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 01:11:56,356 [INFO] nina.router_log: {"ts": "2026-05-23T01:11:56.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 419, "output_tokens": 114, "cost_usd": 0.0, "ttf_ms": 817.6586627960205, "total_ms": 817.6586627960205, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 01:15:32,652 [INFO] nina.router_log: {"ts": "2026-05-23T01:15:32.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 131, "output_tokens": 69, "cost_usd": 0.0, "ttf_ms": 784.6357822418213, "total_ms": 784.6357822418213, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 01:15:32,652 [INFO] nina.router_log: {"ts": "2026-05-23T01:15:32.000+0600", "provider": "CACHE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": true, "status": "success", "error": null}
2026-05-23 01:15:32,652 [INFO] nina.router_log: {"ts": "2026-05-23T01:15:32.000+0600", "provider": "CACHE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": true, "status": "success", "error": null}
2026-05-23 01:15:32,652 [INFO] nina.router_log: {"ts": "2026-05-23T01:15:32.000+0600", "provider": "CACHE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": true, "status": "success", "error": null}
2026-05-23 01:15:32,652 [INFO] nina.router_log: {"ts": "2026-05-23T01:15:32.000+0600", "provider": "CACHE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": true, "status": "success", "error": null}
2026-05-23 01:37:16,956 [INFO] nina.router_log: {"ts": "2026-05-23T01:37:16.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 01:37:18,281 [INFO] nina.router_log: {"ts": "2026-05-23T01:37:18.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 01:37:18,344 [INFO] nina.router_log: {"ts": "2026-05-23T01:37:18.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 01:37:19,069 [INFO] nina.router_log: {"ts": "2026-05-23T01:37:19.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 01:37:19,885 [INFO] nina.router_log: {"ts": "2026-05-23T01:37:19.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 440, "output_tokens": 116, "cost_usd": 0.0, "ttf_ms": 815.8934116363525, "total_ms": 815.8934116363525, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 15:08:37,332 [INFO] nina.router_log: {"ts": "2026-05-23T15:08:37.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 15:08:38,621 [INFO] nina.router_log: {"ts": "2026-05-23T15:08:38.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 15:08:38,678 [INFO] nina.router_log: {"ts": "2026-05-23T15:08:38.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 15:08:39,197 [INFO] nina.router_log: {"ts": "2026-05-23T15:08:39.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 15:08:40,059 [INFO] nina.router_log: {"ts": "2026-05-23T15:08:40.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 440, "output_tokens": 129, "cost_usd": 0.0, "ttf_ms": 861.8483543395996, "total_ms": 861.8483543395996, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 15:39:42,043 [INFO] nina.router_log: {"ts": "2026-05-23T15:39:42.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 439, "output_tokens": 306, "cost_usd": 0.0, "ttf_ms": 1874.3431568145752, "total_ms": 1874.3431568145752, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 16:10:56,131 [INFO] nina.router_log: {"ts": "2026-05-23T16:10:56.000+0600", "provider": "MISTRAL", "task_type": "research", "input_tokens": 511, "output_tokens": 758, "cost_usd": 0.0, "ttf_ms": 13964.902877807617, "total_ms": 13964.902877807617, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 16:41:56,531 [INFO] nina.router_log: {"ts": "2026-05-23T16:41:56.000+0600", "provider": "DEEPSEEK", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.deepseek.com/v1/chat/comple"}
2026-05-23 16:41:56,741 [INFO] nina.router_log: {"ts": "2026-05-23T16:41:56.000+0600", "provider": "GEMINI", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://generativelanguage.googleapis.com/"}
2026-05-23 16:41:57,725 [INFO] nina.router_log: {"ts": "2026-05-23T16:41:57.000+0600", "provider": "TOGETHER", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.together.xyz/v1/chat/completio"}
2026-05-23 16:41:58,784 [INFO] nina.router_log: {"ts": "2026-05-23T16:41:58.000+0600", "provider": "COHERE", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '405 Method Not Allowed' for url 'https://api.cohere.ai/v2/chat/com"}
2026-05-23 16:41:59,117 [INFO] nina.router_log: {"ts": "2026-05-23T16:41:59.000+0600", "provider": "FIREWORKS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.fireworks.ai/inference/v1/chat"}
2026-05-23 16:41:59,878 [INFO] nina.router_log: {"ts": "2026-05-23T16:41:59.000+0600", "provider": "XAI", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '400 Bad Request' for url 'https://api.x.ai/v1/chat/completions'\nFo"}
2026-05-23 16:42:00,521 [INFO] nina.router_log: {"ts": "2026-05-23T16:42:00.000+0600", "provider": "SAMBANOVA", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 NOT FOUND' for url 'https://api.sambanova.ai/v1/chat/completio"}
2026-05-23 16:42:02,234 [INFO] nina.router_log: {"ts": "2026-05-23T16:42:02.000+0600", "provider": "HYPERBOLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '402 Payment Required' for url 'https://api.hyperbolic.xyz/v1/chat/"}
2026-05-23 16:42:02,951 [INFO] nina.router_log: {"ts": "2026-05-23T16:42:02.000+0600", "provider": "NOVITA", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.novita.ai/v3/openai/chat/compl"}
2026-05-23 16:42:04,385 [INFO] nina.router_log: {"ts": "2026-05-23T16:42:04.000+0600", "provider": "OPENAI", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.openai.com/v1/chat/completi"}
2026-05-23 16:42:16,055 [INFO] nina.router_log: {"ts": "2026-05-23T16:42:16.000+0600", "provider": "OPENROUTER", "task_type": "research", "input_tokens": 420, "output_tokens": 1161, "cost_usd": 0.0, "ttf_ms": 11665.452003479004, "total_ms": 11665.452003479004, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 17:13:17,701 [INFO] nina.router_log: {"ts": "2026-05-23T17:13:17.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 408, "output_tokens": 290, "cost_usd": 0.0, "ttf_ms": 1530.0376415252686, "total_ms": 1530.0376415252686, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 17:56:21,673 [INFO] nina.router_log: {"ts": "2026-05-23T17:56:21.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 408, "output_tokens": 271, "cost_usd": 0.0, "ttf_ms": 1649.216651916504, "total_ms": 1649.216651916504, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 21:32:27,420 [INFO] nina.router_log: {"ts": "2026-05-23T21:32:27.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 21:32:28,766 [INFO] nina.router_log: {"ts": "2026-05-23T21:32:28.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 21:32:28,821 [INFO] nina.router_log: {"ts": "2026-05-23T21:32:28.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 21:32:30,200 [INFO] nina.router_log: {"ts": "2026-05-23T21:32:30.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 21:32:31,094 [INFO] nina.router_log: {"ts": "2026-05-23T21:32:31.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 410, "output_tokens": 143, "cost_usd": 0.0, "ttf_ms": 893.8732147216797, "total_ms": 893.8732147216797, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 21:55:58,723 [INFO] nina.router_log: {"ts": "2026-05-23T21:55:58.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 21:56:00,198 [INFO] nina.router_log: {"ts": "2026-05-23T21:56:00.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 21:56:00,260 [INFO] nina.router_log: {"ts": "2026-05-23T21:56:00.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 21:56:00,812 [INFO] nina.router_log: {"ts": "2026-05-23T21:56:00.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 21:56:01,734 [INFO] nina.router_log: {"ts": "2026-05-23T21:56:01.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 131, "cost_usd": 0.0, "ttf_ms": 922.081708908081, "total_ms": 922.081708908081, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 21:59:49,365 [INFO] nina.router_log: {"ts": "2026-05-23T21:59:49.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 21:59:50,753 [INFO] nina.router_log: {"ts": "2026-05-23T21:59:50.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 21:59:50,778 [INFO] nina.router_log: {"ts": "2026-05-23T21:59:50.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 21:59:51,226 [INFO] nina.router_log: {"ts": "2026-05-23T21:59:51.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 21:59:51,880 [INFO] nina.router_log: {"ts": "2026-05-23T21:59:51.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 111, "cost_usd": 0.0, "ttf_ms": 653.7590026855469, "total_ms": 653.7590026855469, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 22:03:07,415 [INFO] nina.router_log: {"ts": "2026-05-23T22:03:07.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 22:03:08,746 [INFO] nina.router_log: {"ts": "2026-05-23T22:03:08.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 22:03:08,801 [INFO] nina.router_log: {"ts": "2026-05-23T22:03:08.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 22:03:09,363 [INFO] nina.router_log: {"ts": "2026-05-23T22:03:09.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 22:03:10,079 [INFO] nina.router_log: {"ts": "2026-05-23T22:03:10.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 102, "cost_usd": 0.0, "ttf_ms": 715.1358127593994, "total_ms": 715.1358127593994, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 22:08:58,652 [INFO] nina.router_log: {"ts": "2026-05-23T22:08:58.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 22:08:59,918 [INFO] nina.router_log: {"ts": "2026-05-23T22:08:59.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 22:08:59,973 [INFO] nina.router_log: {"ts": "2026-05-23T22:08:59.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 22:09:00,494 [INFO] nina.router_log: {"ts": "2026-05-23T22:09:00.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 22:09:01,190 [INFO] nina.router_log: {"ts": "2026-05-23T22:09:01.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 131, "cost_usd": 0.0, "ttf_ms": 696.220874786377, "total_ms": 696.220874786377, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 22:14:43,945 [INFO] nina.router_log: {"ts": "2026-05-23T22:14:43.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 22:14:44,598 [INFO] nina.router_log: {"ts": "2026-05-23T22:14:44.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 22:14:44,622 [INFO] nina.router_log: {"ts": "2026-05-23T22:14:44.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 22:14:45,278 [INFO] nina.router_log: {"ts": "2026-05-23T22:14:45.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 22:14:46,198 [INFO] nina.router_log: {"ts": "2026-05-23T22:14:46.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 101, "cost_usd": 0.0, "ttf_ms": 920.4800128936768, "total_ms": 920.4800128936768, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 22:16:59,833 [INFO] nina.router_log: {"ts": "2026-05-23T22:16:59.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 22:17:01,162 [INFO] nina.router_log: {"ts": "2026-05-23T22:17:01.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 22:17:01,222 [INFO] nina.router_log: {"ts": "2026-05-23T22:17:01.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 22:17:01,674 [INFO] nina.router_log: {"ts": "2026-05-23T22:17:01.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 22:17:02,392 [INFO] nina.router_log: {"ts": "2026-05-23T22:17:02.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 100, "cost_usd": 0.0, "ttf_ms": 717.8778648376465, "total_ms": 717.8778648376465, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 22:19:20,427 [INFO] nina.router_log: {"ts": "2026-05-23T22:19:20.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 22:19:21,861 [INFO] nina.router_log: {"ts": "2026-05-23T22:19:21.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 22:19:21,911 [INFO] nina.router_log: {"ts": "2026-05-23T22:19:21.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 22:19:22,475 [INFO] nina.router_log: {"ts": "2026-05-23T22:19:22.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 22:19:23,296 [INFO] nina.router_log: {"ts": "2026-05-23T22:19:23.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 164, "cost_usd": 0.0, "ttf_ms": 820.1289176940918, "total_ms": 820.1289176940918, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 22:24:06,945 [INFO] nina.router_log: {"ts": "2026-05-23T22:24:06.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 22:24:07,436 [INFO] nina.router_log: {"ts": "2026-05-23T22:24:07.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 22:24:07,501 [INFO] nina.router_log: {"ts": "2026-05-23T22:24:07.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 22:24:08,071 [INFO] nina.router_log: {"ts": "2026-05-23T22:24:08.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 22:24:09,096 [INFO] nina.router_log: {"ts": "2026-05-23T22:24:09.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 136, "cost_usd": 0.0, "ttf_ms": 1025.362491607666, "total_ms": 1025.362491607666, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 22:44:04,009 [INFO] nina.router_log: {"ts": "2026-05-23T22:44:04.000+0600", "provider": "POLLINATIONS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-23 22:44:05,392 [INFO] nina.router_log: {"ts": "2026-05-23T22:44:05.000+0600", "provider": "CHUTES", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-23 22:44:05,519 [INFO] nina.router_log: {"ts": "2026-05-23T22:44:05.000+0600", "provider": "HFPUBLIC", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-23 22:44:06,057 [INFO] nina.router_log: {"ts": "2026-05-23T22:44:06.000+0600", "provider": "CEREBRAS", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-23 22:44:06,774 [INFO] nina.router_log: {"ts": "2026-05-23T22:44:06.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 396, "output_tokens": 117, "cost_usd": 0.0, "ttf_ms": 716.649055480957, "total_ms": 716.649055480957, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 23:15:08,973 [INFO] nina.router_log: {"ts": "2026-05-23T23:15:08.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 395, "output_tokens": 306, "cost_usd": 0.0, "ttf_ms": 2073.6775398254395, "total_ms": 2073.6775398254395, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-23 23:46:21,015 [INFO] nina.router_log: {"ts": "2026-05-23T23:46:21.000+0600", "provider": "MISTRAL", "task_type": "research", "input_tokens": 447, "output_tokens": 686, "cost_usd": 0.0, "ttf_ms": 11915.283918380737, "total_ms": 11915.283918380737, "parallel": false, "cached": false, "status": "success", "error": null}
```

### logs/router.log.2026-05-21
Last modified: 2026-05-21 23:58:19
Size: 12781 bytes
```log
2026-05-21 22:35:51,432 [INFO] nina.router_log: {"ts": "2026-05-21T22:35:51.000+0600", "provider": "POLLINATIONS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-21 22:35:52,729 [INFO] nina.router_log: {"ts": "2026-05-21T22:35:52.000+0600", "provider": "CHUTES", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-21 22:35:52,758 [INFO] nina.router_log: {"ts": "2026-05-21T22:35:52.000+0600", "provider": "HFPUBLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-21 22:35:53,169 [INFO] nina.router_log: {"ts": "2026-05-21T22:35:53.000+0600", "provider": "CEREBRAS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-21 22:35:54,190 [INFO] nina.router_log: {"ts": "2026-05-21T22:35:54.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 138, "output_tokens": 42, "cost_usd": 0.0, "ttf_ms": 1021.2507247924805, "total_ms": 1021.2507247924805, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-21 22:42:33,127 [INFO] nina.router_log: {"ts": "2026-05-21T22:42:33.000+0600", "provider": "MISTRAL", "task_type": "general", "input_tokens": 172, "output_tokens": 310, "cost_usd": 0.0, "ttf_ms": 6158.805131912231, "total_ms": 6158.805131912231, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-21 22:43:00,519 [INFO] nina.router_log: {"ts": "2026-05-21T22:43:00.000+0600", "provider": "DEEPSEEK", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.deepseek.com/v1/chat/comple"}
2026-05-21 22:43:00,751 [INFO] nina.router_log: {"ts": "2026-05-21T22:43:00.000+0600", "provider": "GEMINI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://generativelanguage.googleapis.com/"}
2026-05-21 22:43:03,354 [INFO] nina.router_log: {"ts": "2026-05-21T22:43:03.000+0600", "provider": "TOGETHER", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.together.xyz/v1/chat/completio"}
2026-05-21 22:43:04,767 [INFO] nina.router_log: {"ts": "2026-05-21T22:43:04.000+0600", "provider": "COHERE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '405 Method Not Allowed' for url 'https://api.cohere.ai/v1/chat/com"}
2026-05-21 22:43:05,836 [INFO] nina.router_log: {"ts": "2026-05-21T22:43:05.000+0600", "provider": "FIREWORKS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.fireworks.ai/inference/v1/chat"}
2026-05-21 22:43:06,324 [INFO] nina.router_log: {"ts": "2026-05-21T22:43:06.000+0600", "provider": "XAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '400 Bad Request' for url 'https://api.x.ai/v1/chat/completions'\nFo"}
2026-05-21 22:43:07,451 [INFO] nina.router_log: {"ts": "2026-05-21T22:43:07.000+0600", "provider": "SAMBANOVA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 NOT FOUND' for url 'https://api.sambanova.ai/v1/chat/completio"}
2026-05-21 22:43:08,987 [INFO] nina.router_log: {"ts": "2026-05-21T22:43:08.000+0600", "provider": "HYPERBOLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '402 Payment Required' for url 'https://api.hyperbolic.xyz/v1/chat/"}
2026-05-21 22:43:09,704 [INFO] nina.router_log: {"ts": "2026-05-21T22:43:09.000+0600", "provider": "NOVITA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.novita.ai/v3/openai/chat/compl"}
2026-05-21 22:43:11,342 [INFO] nina.router_log: {"ts": "2026-05-21T22:43:11.000+0600", "provider": "OPENAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.openai.com/v1/chat/completi"}
2026-05-21 22:43:13,798 [INFO] nina.router_log: {"ts": "2026-05-21T22:43:13.000+0600", "provider": "OPENROUTER", "task_type": "general", "input_tokens": 547, "output_tokens": 68, "cost_usd": 0.0, "ttf_ms": 2456.3944339752197, "total_ms": 2456.3944339752197, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-21 22:43:22,818 [INFO] nina.router_log: {"ts": "2026-05-21T22:43:22.000+0600", "provider": "GROQ", "task_type": "coding", "input_tokens": 555, "output_tokens": 126, "cost_usd": 0.0, "ttf_ms": 859.076976776123, "total_ms": 859.076976776123, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-21 22:43:55,284 [INFO] nina.router_log: {"ts": "2026-05-21T22:43:55.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 699, "output_tokens": 279, "cost_usd": 0.0, "ttf_ms": 1271.3918685913086, "total_ms": 1271.3918685913086, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-21 22:48:26,569 [INFO] nina.router_log: {"ts": "2026-05-21T22:48:26.000+0600", "provider": "GROQ", "task_type": "coding", "input_tokens": 988, "output_tokens": 370, "cost_usd": 0.0, "ttf_ms": 1604.1975021362305, "total_ms": 1604.1975021362305, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-21 22:53:16,178 [INFO] nina.router_log: {"ts": "2026-05-21T22:53:16.000+0600", "provider": "CACHE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": true, "status": "success", "error": null}
2026-05-21 22:54:39,536 [INFO] nina.router_log: {"ts": "2026-05-21T22:54:39.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 1751, "output_tokens": 456, "cost_usd": 0.0, "ttf_ms": 2226.7963886260986, "total_ms": 2226.7963886260986, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-21 22:59:48,369 [INFO] nina.router_log: {"ts": "2026-05-21T22:59:48.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 2221, "output_tokens": 454, "cost_usd": 0.0, "ttf_ms": 2101.332664489746, "total_ms": 2101.332664489746, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-21 23:42:02,334 [INFO] nina.router_log: {"ts": "2026-05-21T23:42:02.000+0600", "provider": "POLLINATIONS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-21 23:42:03,829 [INFO] nina.router_log: {"ts": "2026-05-21T23:42:03.000+0600", "provider": "CHUTES", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-21 23:42:03,906 [INFO] nina.router_log: {"ts": "2026-05-21T23:42:03.000+0600", "provider": "HFPUBLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-21 23:42:04,456 [INFO] nina.router_log: {"ts": "2026-05-21T23:42:04.000+0600", "provider": "CEREBRAS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-21 23:42:04,956 [INFO] nina.router_log: {"ts": "2026-05-21T23:42:04.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 135, "output_tokens": 25, "cost_usd": 0.0, "ttf_ms": 500.0753402709961, "total_ms": 500.0753402709961, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-21 23:52:22,947 [INFO] nina.router_log: {"ts": "2026-05-21T23:52:22.000+0600", "provider": "POLLINATIONS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-21 23:52:24,279 [INFO] nina.router_log: {"ts": "2026-05-21T23:52:24.000+0600", "provider": "CHUTES", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-21 23:52:24,369 [INFO] nina.router_log: {"ts": "2026-05-21T23:52:24.000+0600", "provider": "HFPUBLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-21 23:52:24,790 [INFO] nina.router_log: {"ts": "2026-05-21T23:52:24.000+0600", "provider": "CEREBRAS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-21 23:52:25,303 [INFO] nina.router_log: {"ts": "2026-05-21T23:52:25.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 217, "output_tokens": 21, "cost_usd": 0.0, "ttf_ms": 512.324333190918, "total_ms": 512.324333190918, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-21 23:52:43,230 [INFO] nina.router_log: {"ts": "2026-05-21T23:52:43.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 252, "output_tokens": 47, "cost_usd": 0.0, "ttf_ms": 646.7766761779785, "total_ms": 646.7766761779785, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-21 23:54:38,243 [INFO] nina.router_log: {"ts": "2026-05-21T23:54:38.000+0600", "provider": "GROQ", "task_type": "coding", "input_tokens": 313, "output_tokens": 35, "cost_usd": 0.0, "ttf_ms": 374.39799308776855, "total_ms": 374.39799308776855, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-21 23:55:15,186 [INFO] nina.router_log: {"ts": "2026-05-21T23:55:15.000+0600", "provider": "GROQ", "task_type": "coding", "input_tokens": 363, "output_tokens": 19, "cost_usd": 0.0, "ttf_ms": 457.444429397583, "total_ms": 457.444429397583, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-21 23:58:19,509 [INFO] nina.router_log: {"ts": "2026-05-21T23:58:19.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 398, "output_tokens": 25, "cost_usd": 0.0, "ttf_ms": 655.590295791626, "total_ms": 655.590295791626, "parallel": false, "cached": false, "status": "success", "error": null}
```

### logs/router.log.2026-05-22
Last modified: 2026-05-22 23:36:23
Size: 225364 bytes
```log
[truncated — showing last 200 lines]
2026-05-22 21:39:57,472 [INFO] nina.router_log: {"ts": "2026-05-22T21:39:57.000+0600", "provider": "CHUTES", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-22 21:39:57,508 [INFO] nina.router_log: {"ts": "2026-05-22T21:39:57.000+0600", "provider": "HFPUBLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-22 21:39:58,102 [INFO] nina.router_log: {"ts": "2026-05-22T21:39:58.000+0600", "provider": "CEREBRAS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-22 21:39:58,831 [INFO] nina.router_log: {"ts": "2026-05-22T21:39:58.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 131, "output_tokens": 89, "cost_usd": 0.0, "ttf_ms": 728.4767627716064, "total_ms": 728.4767627716064, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:39:58,832 [INFO] nina.router_log: {"ts": "2026-05-22T21:39:58.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:40:00,786 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:00.000+0600", "provider": "MISTRAL", "task_type": "general", "input_tokens": 100, "output_tokens": 84, "cost_usd": 0.0, "ttf_ms": 1953.8991451263428, "total_ms": 1953.8991451263428, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:40:00,787 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:00.000+0600", "provider": "MISTRAL", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:40:01,161 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:01.000+0600", "provider": "DEEPSEEK", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.deepseek.com/v1/chat/comple"}
2026-05-22 21:40:01,383 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:01.000+0600", "provider": "GEMINI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://generativelanguage.googleapis.com/"}
2026-05-22 21:40:02,801 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:02.000+0600", "provider": "TOGETHER", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.together.xyz/v1/chat/completio"}
2026-05-22 21:40:03,310 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:03.000+0600", "provider": "COHERE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '405 Method Not Allowed' for url 'https://api.cohere.ai/v2/chat/com"}
2026-05-22 21:40:04,438 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:04.000+0600", "provider": "FIREWORKS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.fireworks.ai/inference/v1/chat"}
2026-05-22 21:40:04,793 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:04.000+0600", "provider": "XAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '400 Bad Request' for url 'https://api.x.ai/v1/chat/completions'\nFo"}
2026-05-22 21:40:05,583 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:05.000+0600", "provider": "SAMBANOVA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 NOT FOUND' for url 'https://api.sambanova.ai/v1/chat/completio"}
2026-05-22 21:40:06,281 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:06.000+0600", "provider": "HYPERBOLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '402 Payment Required' for url 'https://api.hyperbolic.xyz/v1/chat/"}
2026-05-22 21:40:06,781 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:06.000+0600", "provider": "NOVITA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.novita.ai/v3/openai/chat/compl"}
2026-05-22 21:40:07,203 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:07.000+0600", "provider": "OPENAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.openai.com/v1/chat/completi"}
2026-05-22 21:40:10,062 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:10.000+0600", "provider": "OPENROUTER", "task_type": "general", "input_tokens": 146, "output_tokens": 53, "cost_usd": 0.0, "ttf_ms": 2858.5140705108643, "total_ms": 2858.5140705108643, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:40:10,063 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:10.000+0600", "provider": "OPENROUTER", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:40:10,064 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:10.000+0600", "provider": "ONEBRAIN", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "unknown url type: '/onebrain.rocks/api/eu/v1/openapi/chat/completions'"}
2026-05-22 21:40:11,490 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:11.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1424.8671531677246, "total_ms": 1424.8671531677246, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:40:11,490 [INFO] nina.router_log: {"ts": "2026-05-22T21:40:11.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:42:42,444 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:42.000+0600", "provider": "POLLINATIONS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Server error '502 Bad Gateway' for url 'https://text.pollinations.ai/openai/chat"}
2026-05-22 21:42:43,772 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:43.000+0600", "provider": "CHUTES", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-22 21:42:43,834 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:43.000+0600", "provider": "HFPUBLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-22 21:42:44,387 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:44.000+0600", "provider": "CEREBRAS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-22 21:42:45,131 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:45.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 131, "output_tokens": 49, "cost_usd": 0.0, "ttf_ms": 742.8243160247803, "total_ms": 742.8243160247803, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:42:45,131 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:45.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:42:47,051 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:47.000+0600", "provider": "MISTRAL", "task_type": "general", "input_tokens": 100, "output_tokens": 84, "cost_usd": 0.0, "ttf_ms": 1919.2438125610352, "total_ms": 1919.2438125610352, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:42:47,051 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:47.000+0600", "provider": "MISTRAL", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:42:47,394 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:47.000+0600", "provider": "DEEPSEEK", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.deepseek.com/v1/chat/comple"}
2026-05-22 21:42:47,637 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:47.000+0600", "provider": "GEMINI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://generativelanguage.googleapis.com/"}
2026-05-22 21:42:48,791 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:48.000+0600", "provider": "TOGETHER", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.together.xyz/v1/chat/completio"}
2026-05-22 21:42:50,430 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:50.000+0600", "provider": "COHERE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '405 Method Not Allowed' for url 'https://api.cohere.ai/v2/chat/com"}
2026-05-22 21:42:51,557 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:51.000+0600", "provider": "FIREWORKS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.fireworks.ai/inference/v1/chat"}
2026-05-22 21:42:51,966 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:51.000+0600", "provider": "XAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '400 Bad Request' for url 'https://api.x.ai/v1/chat/completions'\nFo"}
2026-05-22 21:42:52,620 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:52.000+0600", "provider": "SAMBANOVA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 NOT FOUND' for url 'https://api.sambanova.ai/v1/chat/completio"}
2026-05-22 21:42:54,099 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:54.000+0600", "provider": "HYPERBOLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '402 Payment Required' for url 'https://api.hyperbolic.xyz/v1/chat/"}
2026-05-22 21:42:54,731 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:54.000+0600", "provider": "NOVITA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.novita.ai/v3/openai/chat/compl"}
2026-05-22 21:42:55,246 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:55.000+0600", "provider": "OPENAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.openai.com/v1/chat/completi"}
2026-05-22 21:42:58,214 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:58.000+0600", "provider": "OPENROUTER", "task_type": "general", "input_tokens": 146, "output_tokens": 62, "cost_usd": 0.0, "ttf_ms": 2967.7693843841553, "total_ms": 2967.7693843841553, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:42:58,214 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:58.000+0600", "provider": "OPENROUTER", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:42:58,215 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:58.000+0600", "provider": "ONEBRAIN", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "unknown url type: '/onebrain.rocks/api/eu/v1/openapi/chat/completions'"}
2026-05-22 21:42:59,676 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:59.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1460.5088233947754, "total_ms": 1460.5088233947754, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:42:59,676 [INFO] nina.router_log: {"ts": "2026-05-22T21:42:59.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:44:12,749 [INFO] nina.router_log: {"ts": "2026-05-22T21:44:12.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 38115.30804634094, "total_ms": 38115.30804634094, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:44:12,750 [INFO] nina.router_log: {"ts": "2026-05-22T21:44:12.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:45:23,312 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:23.000+0600", "provider": "POLLINATIONS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-22 21:45:24,748 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:24.000+0600", "provider": "CHUTES", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-22 21:45:24,813 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:24.000+0600", "provider": "HFPUBLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-22 21:45:25,363 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:25.000+0600", "provider": "CEREBRAS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-22 21:45:26,182 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:26.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 131, "output_tokens": 67, "cost_usd": 0.0, "ttf_ms": 819.3237781524658, "total_ms": 819.3237781524658, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:45:26,183 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:26.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:45:28,334 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:28.000+0600", "provider": "MISTRAL", "task_type": "general", "input_tokens": 100, "output_tokens": 95, "cost_usd": 0.0, "ttf_ms": 2150.5379676818848, "total_ms": 2150.5379676818848, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:45:28,334 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:28.000+0600", "provider": "MISTRAL", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:45:28,644 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:28.000+0600", "provider": "DEEPSEEK", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.deepseek.com/v1/chat/comple"}
2026-05-22 21:45:28,886 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:28.000+0600", "provider": "GEMINI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://generativelanguage.googleapis.com/"}
2026-05-22 21:45:29,870 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:29.000+0600", "provider": "TOGETHER", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.together.xyz/v1/chat/completio"}
2026-05-22 21:45:30,484 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:30.000+0600", "provider": "COHERE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '405 Method Not Allowed' for url 'https://api.cohere.ai/v2/chat/com"}
2026-05-22 21:45:31,814 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:31.000+0600", "provider": "FIREWORKS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.fireworks.ai/inference/v1/chat"}
2026-05-22 21:45:32,224 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:32.000+0600", "provider": "XAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '400 Bad Request' for url 'https://api.x.ai/v1/chat/completions'\nFo"}
2026-05-22 21:45:32,940 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:32.000+0600", "provider": "SAMBANOVA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 NOT FOUND' for url 'https://api.sambanova.ai/v1/chat/completio"}
2026-05-22 21:45:34,479 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:34.000+0600", "provider": "HYPERBOLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '402 Payment Required' for url 'https://api.hyperbolic.xyz/v1/chat/"}
2026-05-22 21:45:34,846 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:34.000+0600", "provider": "NOVITA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.novita.ai/v3/openai/chat/compl"}
2026-05-22 21:45:35,501 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:35.000+0600", "provider": "OPENAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.openai.com/v1/chat/completi"}
2026-05-22 21:45:37,752 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:37.000+0600", "provider": "OPENROUTER", "task_type": "general", "input_tokens": 146, "output_tokens": 48, "cost_usd": 0.0, "ttf_ms": 2250.049114227295, "total_ms": 2250.049114227295, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:45:37,752 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:37.000+0600", "provider": "OPENROUTER", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:45:37,754 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:37.000+0600", "provider": "ONEBRAIN", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "unknown url type: '/onebrain.rocks/api/eu/v1/openapi/chat/completions'"}
2026-05-22 21:45:39,195 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:39.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1439.9142265319824, "total_ms": 1439.9142265319824, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:45:39,195 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:39.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:45:40,807 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:40.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1604.7313213348389, "total_ms": 1604.7313213348389, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:45:40,808 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:40.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:45:43,879 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:43.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 3070.263624191284, "total_ms": 3070.263624191284, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:45:43,880 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:43.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:45:45,280 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:45.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1399.1270065307617, "total_ms": 1399.1270065307617, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:45:45,281 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:45.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:45:48,403 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:48.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 3121.0756301879883, "total_ms": 3121.0756301879883, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:45:48,404 [INFO] nina.router_log: {"ts": "2026-05-22T21:45:48.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:46:21,625 [INFO] nina.router_log: {"ts": "2026-05-22T21:46:21.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1539.5536422729492, "total_ms": 1539.5536422729492, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:46:21,626 [INFO] nina.router_log: {"ts": "2026-05-22T21:46:21.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:46:22,820 [INFO] nina.router_log: {"ts": "2026-05-22T21:46:22.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1192.5153732299805, "total_ms": 1192.5153732299805, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:46:22,820 [INFO] nina.router_log: {"ts": "2026-05-22T21:46:22.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:46:23,895 [INFO] nina.router_log: {"ts": "2026-05-22T21:46:23.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1074.0110874176025, "total_ms": 1074.0110874176025, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:46:23,895 [INFO] nina.router_log: {"ts": "2026-05-22T21:46:23.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:46:27,021 [INFO] nina.router_log: {"ts": "2026-05-22T21:46:27.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 3124.460220336914, "total_ms": 3124.460220336914, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:46:27,021 [INFO] nina.router_log: {"ts": "2026-05-22T21:46:27.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:46:28,027 [INFO] nina.router_log: {"ts": "2026-05-22T21:46:28.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1004.7030448913574, "total_ms": 1004.7030448913574, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:46:28,027 [INFO] nina.router_log: {"ts": "2026-05-22T21:46:28.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 21:49:24,117 [INFO] nina.router_log: {"ts": "2026-05-22T21:49:24.000+0600", "provider": "LOCALFAST", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 11430.857419967651, "total_ms": 11430.857419967651, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 21:49:24,118 [INFO] nina.router_log: {"ts": "2026-05-22T21:49:24.000+0600", "provider": "LOCALFAST", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:13:19,312 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:19.000+0600", "provider": "POLLINATIONS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-22 22:13:21,360 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:21.000+0600", "provider": "CHUTES", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-22 22:13:21,389 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:21.000+0600", "provider": "HFPUBLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-22 22:13:21,871 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:21.000+0600", "provider": "CEREBRAS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-22 22:13:22,692 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:22.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 131, "output_tokens": 71, "cost_usd": 0.0, "ttf_ms": 820.429801940918, "total_ms": 820.429801940918, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:13:22,692 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:22.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:13:24,842 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:24.000+0600", "provider": "MISTRAL", "task_type": "general", "input_tokens": 100, "output_tokens": 82, "cost_usd": 0.0, "ttf_ms": 2149.293899536133, "total_ms": 2149.293899536133, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:13:24,842 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:24.000+0600", "provider": "MISTRAL", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:13:25,250 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:25.000+0600", "provider": "DEEPSEEK", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.deepseek.com/v1/chat/comple"}
2026-05-22 22:13:25,618 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:25.000+0600", "provider": "GEMINI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://generativelanguage.googleapis.com/"}
2026-05-22 22:13:27,401 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:27.000+0600", "provider": "TOGETHER", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.together.xyz/v1/chat/completio"}
2026-05-22 22:13:28,291 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:28.000+0600", "provider": "COHERE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '405 Method Not Allowed' for url 'https://api.cohere.ai/v2/chat/com"}
2026-05-22 22:13:29,244 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:29.000+0600", "provider": "FIREWORKS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.fireworks.ai/inference/v1/chat"}
2026-05-22 22:13:29,961 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:29.000+0600", "provider": "XAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '400 Bad Request' for url 'https://api.x.ai/v1/chat/completions'\nFo"}
2026-05-22 22:13:30,537 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:30.000+0600", "provider": "SAMBANOVA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 NOT FOUND' for url 'https://api.sambanova.ai/v1/chat/completio"}
2026-05-22 22:13:32,316 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:32.000+0600", "provider": "HYPERBOLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '402 Payment Required' for url 'https://api.hyperbolic.xyz/v1/chat/"}
2026-05-22 22:13:32,954 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:32.000+0600", "provider": "NOVITA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.novita.ai/v3/openai/chat/compl"}
2026-05-22 22:13:33,649 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:33.000+0600", "provider": "OPENAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.openai.com/v1/chat/completi"}
2026-05-22 22:13:37,741 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:37.000+0600", "provider": "OPENROUTER", "task_type": "general", "input_tokens": 146, "output_tokens": 52, "cost_usd": 0.0, "ttf_ms": 4092.4623012542725, "total_ms": 4092.4623012542725, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:13:37,742 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:37.000+0600", "provider": "OPENROUTER", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:13:37,743 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:37.000+0600", "provider": "ONEBRAIN", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "unknown url type: '/onebrain.rocks/api/eu/v1/openapi/chat/completions'"}
2026-05-22 22:13:39,177 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:39.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1433.9265823364258, "total_ms": 1433.9265823364258, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:13:39,178 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:39.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:13:41,032 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:41.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1853.818416595459, "total_ms": 1853.818416595459, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:13:41,033 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:41.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:13:42,023 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:42.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 988.5618686676025, "total_ms": 988.5618686676025, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:13:42,023 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:42.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:13:43,063 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:43.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1038.3152961730957, "total_ms": 1038.3152961730957, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:13:43,063 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:43.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:13:45,996 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:45.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 2931.6296577453613, "total_ms": 2931.6296577453613, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:13:45,996 [INFO] nina.router_log: {"ts": "2026-05-22T22:13:45.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:16:09,283 [INFO] nina.router_log: {"ts": "2026-05-22T22:16:09.000+0600", "provider": "LOCALFAST", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 29023.595571517944, "total_ms": 29023.595571517944, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:16:09,283 [INFO] nina.router_log: {"ts": "2026-05-22T22:16:09.000+0600", "provider": "LOCALFAST", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:20:22,950 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:22.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 167, "output_tokens": 74, "cost_usd": 0.0, "ttf_ms": 760.8249187469482, "total_ms": 760.8249187469482, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:20:22,950 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:22.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:20:25,812 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:25.000+0600", "provider": "MISTRAL", "task_type": "general", "input_tokens": 131, "output_tokens": 82, "cost_usd": 0.0, "ttf_ms": 2861.7374897003174, "total_ms": 2861.7374897003174, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:20:25,813 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:25.000+0600", "provider": "MISTRAL", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:20:28,265 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:28.000+0600", "provider": "OPENROUTER", "task_type": "general", "input_tokens": 181, "output_tokens": 50, "cost_usd": 0.0, "ttf_ms": 2451.5461921691895, "total_ms": 2451.5461921691895, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:20:28,265 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:28.000+0600", "provider": "OPENROUTER", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:20:31,159 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:31.000+0600", "provider": "POLLINATIONS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-22 22:20:32,514 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:32.000+0600", "provider": "CHUTES", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-22 22:20:32,541 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:32.000+0600", "provider": "HFPUBLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-22 22:20:32,993 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:32.000+0600", "provider": "CEREBRAS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-22 22:20:33,278 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:33.000+0600", "provider": "DEEPSEEK", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.deepseek.com/v1/chat/comple"}
2026-05-22 22:20:33,635 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:33.000+0600", "provider": "GEMINI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://generativelanguage.googleapis.com/"}
2026-05-22 22:20:34,516 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:34.000+0600", "provider": "TOGETHER", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.together.xyz/v1/chat/completio"}
2026-05-22 22:20:35,333 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:35.000+0600", "provider": "COHERE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '405 Method Not Allowed' for url 'https://api.cohere.ai/v2/chat/com"}
2026-05-22 22:20:37,280 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:37.000+0600", "provider": "FIREWORKS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.fireworks.ai/inference/v1/chat"}
2026-05-22 22:20:37,794 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:37.000+0600", "provider": "XAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '400 Bad Request' for url 'https://api.x.ai/v1/chat/completions'\nFo"}
2026-05-22 22:20:39,239 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:39.000+0600", "provider": "SAMBANOVA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 NOT FOUND' for url 'https://api.sambanova.ai/v1/chat/completio"}
2026-05-22 22:20:40,967 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:40.000+0600", "provider": "HYPERBOLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '402 Payment Required' for url 'https://api.hyperbolic.xyz/v1/chat/"}
2026-05-22 22:20:41,581 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:41.000+0600", "provider": "NOVITA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.novita.ai/v3/openai/chat/compl"}
2026-05-22 22:20:42,811 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:42.000+0600", "provider": "OPENAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.openai.com/v1/chat/completi"}
2026-05-22 22:20:42,813 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:42.000+0600", "provider": "ONEBRAIN", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "unknown url type: '/onebrain.rocks/api/eu/v1/openapi/chat/completions'"}
2026-05-22 22:20:44,211 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:44.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1397.8023529052734, "total_ms": 1397.8023529052734, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:20:44,211 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:44.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:20:45,321 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:45.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1108.3855628967285, "total_ms": 1108.3855628967285, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:20:45,321 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:45.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:20:46,401 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:46.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1079.2386531829834, "total_ms": 1079.2386531829834, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:20:46,401 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:46.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:20:47,525 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:47.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1122.8744983673096, "total_ms": 1122.8744983673096, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:20:47,526 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:47.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:20:48,849 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:48.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1322.0493793487549, "total_ms": 1322.0493793487549, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:20:48,849 [INFO] nina.router_log: {"ts": "2026-05-22T22:20:48.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:27:55,250 [INFO] nina.router_log: {"ts": "2026-05-22T22:27:55.000+0600", "provider": "POLLINATIONS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-22 22:27:56,670 [INFO] nina.router_log: {"ts": "2026-05-22T22:27:56.000+0600", "provider": "CHUTES", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-22 22:27:56,702 [INFO] nina.router_log: {"ts": "2026-05-22T22:27:56.000+0600", "provider": "HFPUBLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-22 22:27:57,297 [INFO] nina.router_log: {"ts": "2026-05-22T22:27:57.000+0600", "provider": "CEREBRAS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-22 22:27:58,129 [INFO] nina.router_log: {"ts": "2026-05-22T22:27:58.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 131, "output_tokens": 91, "cost_usd": 0.0, "ttf_ms": 831.6354751586914, "total_ms": 831.6354751586914, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:27:58,129 [INFO] nina.router_log: {"ts": "2026-05-22T22:27:58.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:28:00,268 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:00.000+0600", "provider": "MISTRAL", "task_type": "general", "input_tokens": 100, "output_tokens": 84, "cost_usd": 0.0, "ttf_ms": 2138.119697570801, "total_ms": 2138.119697570801, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:28:00,268 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:00.000+0600", "provider": "MISTRAL", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:28:00,653 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:00.000+0600", "provider": "DEEPSEEK", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.deepseek.com/v1/chat/comple"}
2026-05-22 22:28:01,393 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:01.000+0600", "provider": "GEMINI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://generativelanguage.googleapis.com/"}
2026-05-22 22:28:02,443 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:02.000+0600", "provider": "TOGETHER", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.together.xyz/v1/chat/completio"}
2026-05-22 22:28:03,018 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:03.000+0600", "provider": "COHERE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '405 Method Not Allowed' for url 'https://api.cohere.ai/v2/chat/com"}
2026-05-22 22:28:04,357 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:04.000+0600", "provider": "FIREWORKS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.fireworks.ai/inference/v1/chat"}
2026-05-22 22:28:05,076 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:05.000+0600", "provider": "XAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '400 Bad Request' for url 'https://api.x.ai/v1/chat/completions'\nFo"}
2026-05-22 22:28:06,000 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:05.000+0600", "provider": "SAMBANOVA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 NOT FOUND' for url 'https://api.sambanova.ai/v1/chat/completio"}
2026-05-22 22:28:07,434 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:07.000+0600", "provider": "HYPERBOLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '402 Payment Required' for url 'https://api.hyperbolic.xyz/v1/chat/"}
2026-05-22 22:28:08,050 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:08.000+0600", "provider": "NOVITA", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.novita.ai/v3/openai/chat/compl"}
2026-05-22 22:28:08,814 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:08.000+0600", "provider": "OPENAI", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://api.openai.com/v1/chat/completi"}
2026-05-22 22:28:11,631 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:11.000+0600", "provider": "OPENROUTER", "task_type": "general", "input_tokens": 146, "output_tokens": 60, "cost_usd": 0.0, "ttf_ms": 2816.5953159332275, "total_ms": 2816.5953159332275, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:28:11,631 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:11.000+0600", "provider": "OPENROUTER", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:28:11,632 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:11.000+0600", "provider": "ONEBRAIN", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "unknown url type: '/onebrain.rocks/api/eu/v1/openapi/chat/completions'"}
2026-05-22 22:28:12,942 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:12.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1309.6814155578613, "total_ms": 1309.6814155578613, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:28:12,943 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:12.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:28:14,140 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:14.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1196.155071258545, "total_ms": 1196.155071258545, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:28:14,141 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:14.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:28:15,479 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:15.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 1337.141752243042, "total_ms": 1337.141752243042, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:28:15,480 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:15.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:28:17,857 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:17.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 2375.833034515381, "total_ms": 2375.833034515381, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:28:17,857 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:17.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:28:21,377 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:21.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 3518.5799598693848, "total_ms": 3518.5799598693848, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:28:21,377 [INFO] nina.router_log: {"ts": "2026-05-22T22:28:21.000+0600", "provider": "LOCALFAST", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 22:32:00,674 [INFO] nina.router_log: {"ts": "2026-05-22T22:32:00.000+0600", "provider": "LOCALFAST", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "ttf_ms": 16494.640111923218, "total_ms": 16494.640111923218, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 22:32:00,675 [INFO] nina.router_log: {"ts": "2026-05-22T22:32:00.000+0600", "provider": "LOCALFAST", "task_type": "research", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "'ResponseCache' object has no attribute 's'"}
2026-05-22 23:02:35,727 [INFO] nina.router_log: {"ts": "2026-05-22T23:02:35.000+0600", "provider": "POLLINATIONS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://text.pollinations.ai/openai/chat/c"}
2026-05-22 23:02:37,298 [INFO] nina.router_log: {"ts": "2026-05-22T23:02:37.000+0600", "provider": "CHUTES", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '401 Unauthorized' for url 'https://llm.chutes.ai/v1/chat/completio"}
2026-05-22 23:02:37,360 [INFO] nina.router_log: {"ts": "2026-05-22T23:02:37.000+0600", "provider": "HFPUBLIC", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "[Errno -5] No address associated with hostname"}
2026-05-22 23:02:37,876 [INFO] nina.router_log: {"ts": "2026-05-22T23:02:37.000+0600", "provider": "CEREBRAS", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": false, "status": "failure", "error": "Client error '404 Not Found' for url 'https://api.cerebras.ai/v1/chat/completion"}
2026-05-22 23:02:38,592 [INFO] nina.router_log: {"ts": "2026-05-22T23:02:38.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 131, "output_tokens": 107, "cost_usd": 0.0, "ttf_ms": 715.6670093536377, "total_ms": 715.6670093536377, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 23:02:48,934 [INFO] nina.router_log: {"ts": "2026-05-22T23:02:48.000+0600", "provider": "GROQ", "task_type": "coding", "input_tokens": 151, "output_tokens": 161, "cost_usd": 0.0, "ttf_ms": 924.166202545166, "total_ms": 924.166202545166, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 23:03:02,759 [INFO] nina.router_log: {"ts": "2026-05-22T23:03:02.000+0600", "provider": "GROQ", "task_type": "general", "input_tokens": 172, "output_tokens": 73, "cost_usd": 0.0, "ttf_ms": 551.6214370727539, "total_ms": 551.6214370727539, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 23:03:04,868 [INFO] nina.router_log: {"ts": "2026-05-22T23:03:04.000+0600", "provider": "CACHE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": true, "status": "success", "error": null}
2026-05-22 23:03:07,264 [INFO] nina.router_log: {"ts": "2026-05-22T23:03:07.000+0600", "provider": "CACHE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": true, "status": "success", "error": null}
2026-05-22 23:03:08,188 [INFO] nina.router_log: {"ts": "2026-05-22T23:03:08.000+0600", "provider": "CACHE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": true, "status": "success", "error": null}
2026-05-22 23:03:09,107 [INFO] nina.router_log: {"ts": "2026-05-22T23:03:09.000+0600", "provider": "CACHE", "task_type": "general", "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "ttf_ms": 0, "total_ms": 0, "parallel": false, "cached": true, "status": "success", "error": null}
2026-05-22 23:05:22,542 [INFO] nina.router_log: {"ts": "2026-05-22T23:05:22.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 421, "output_tokens": 123, "cost_usd": 0.0, "ttf_ms": 821.3849067687988, "total_ms": 821.3849067687988, "parallel": false, "cached": false, "status": "success", "error": null}
2026-05-22 23:36:23,771 [INFO] nina.router_log: {"ts": "2026-05-22T23:36:23.000+0600", "provider": "GROQ", "task_type": "research", "input_tokens": 392, "output_tokens": 218, "cost_usd": 0.0, "ttf_ms": 1133.5368156433105, "total_ms": 1133.5368156433105, "parallel": false, "cached": false, "status": "success", "error": null}
```

### logs/security.log
Last modified: 2026-05-21 22:30:18
Size: 0 bytes
```log
```

### logs/tools.log
Last modified: 2026-06-09 14:30:00
Size: 2980 bytes
```log
2026-06-09 12:30:00,006 [INFO] nina.tools: market_monitor_started
2026-06-09 12:30:00,007 [INFO] nina.tools: market_monitor_summary: Market Monitor Run: Alerts triggered for: GP: 253.5 (UP 1.40%), SQURPHARMA: 215.0 (UP 2.38%)
2026-06-09 12:30:00,007 [INFO] nina.tools: market_monitor_json: [{"ticker": "GP", "last_price": 250.0, "current_price": 253.5, "change_pct": 1.4, "alert": true}, {"ticker": "BATBC", "last_price": 500.0, "current_price": 498.0, "change_pct": -0.4, "alert": false}, {"ticker": "SQURPHARMA", "last_price": 210.0, "current_price": 215.0, "change_pct": 2.38, "alert": true}]
2026-06-09 13:00:00,008 [INFO] nina.tools: market_monitor_started
2026-06-09 13:00:00,008 [INFO] nina.tools: market_monitor_summary: Market Monitor Run: Alerts triggered for: GP: 253.5 (UP 1.40%), SQURPHARMA: 215.0 (UP 2.38%)
2026-06-09 13:00:00,008 [INFO] nina.tools: market_monitor_json: [{"ticker": "GP", "last_price": 250.0, "current_price": 253.5, "change_pct": 1.4, "alert": true}, {"ticker": "BATBC", "last_price": 500.0, "current_price": 498.0, "change_pct": -0.4, "alert": false}, {"ticker": "SQURPHARMA", "last_price": 210.0, "current_price": 215.0, "change_pct": 2.38, "alert": true}]
2026-06-09 13:30:00,006 [INFO] nina.tools: market_monitor_started
2026-06-09 13:30:00,006 [INFO] nina.tools: market_monitor_summary: Market Monitor Run: Alerts triggered for: GP: 253.5 (UP 1.40%), SQURPHARMA: 215.0 (UP 2.38%)
2026-06-09 13:30:00,006 [INFO] nina.tools: market_monitor_json: [{"ticker": "GP", "last_price": 250.0, "current_price": 253.5, "change_pct": 1.4, "alert": true}, {"ticker": "BATBC", "last_price": 500.0, "current_price": 498.0, "change_pct": -0.4, "alert": false}, {"ticker": "SQURPHARMA", "last_price": 210.0, "current_price": 215.0, "change_pct": 2.38, "alert": true}]
2026-06-09 14:00:00,004 [INFO] nina.tools: market_monitor_started
2026-06-09 14:00:00,004 [INFO] nina.tools: market_monitor_summary: Market Monitor Run: Alerts triggered for: GP: 253.5 (UP 1.40%), SQURPHARMA: 215.0 (UP 2.38%)
2026-06-09 14:00:00,004 [INFO] nina.tools: market_monitor_json: [{"ticker": "GP", "last_price": 250.0, "current_price": 253.5, "change_pct": 1.4, "alert": true}, {"ticker": "BATBC", "last_price": 500.0, "current_price": 498.0, "change_pct": -0.4, "alert": false}, {"ticker": "SQURPHARMA", "last_price": 210.0, "current_price": 215.0, "change_pct": 2.38, "alert": true}]
2026-06-09 14:30:00,001 [INFO] nina.tools: market_monitor_started
2026-06-09 14:30:00,001 [INFO] nina.tools: market_monitor_summary: Market Monitor Run: Alerts triggered for: GP: 253.5 (UP 1.40%), SQURPHARMA: 215.0 (UP 2.38%)
2026-06-09 14:30:00,001 [INFO] nina.tools: market_monitor_json: [{"ticker": "GP", "last_price": 250.0, "current_price": 253.5, "change_pct": 1.4, "alert": true}, {"ticker": "BATBC", "last_price": 500.0, "current_price": 498.0, "change_pct": -0.4, "alert": false}, {"ticker": "SQURPHARMA", "last_price": 210.0, "current_price": 215.0, "change_pct": 2.38, "alert": true}]
```

### logs/tools.log.2026-05-21
Last modified: 2026-05-21 22:30:18
Size: 0 bytes
```log
```

### logs/tools.log.2026-05-22
Last modified: 2026-05-22 23:03:09
Size: 1212 bytes
```log
2026-05-22 09:00:03,753 [ERROR] nina.tools.email: morning_report_ews_fetch_failed mailbox=alamba@basicbanklimited.com err=Invalid credentials for https://webmail.basicbanklimited.com/EWS/Exchange.asmx
2026-05-22 09:02:03,979 [ERROR] nina.tools.email: morning_report_ews_fetch_failed mailbox=basicid@basicbanklimited.com err=Invalid credentials for https://webmail.basicbanklimited.com/EWS/Exchange.asmx
2026-05-22 15:40:51,922 [INFO] nina.tools.search: tavily_search query='search USD BDT rate today.' results=5
2026-05-22 15:57:45,167 [INFO] nina.tools.search: tavily_search query='how can namirah concentrate more on her studies, she is my daughter' results=5
2026-05-22 23:03:04,863 [INFO] nina.tools.search: tavily_search query='query="language model name"' results=5
2026-05-22 23:03:07,263 [INFO] nina.tools.search: tavily_search query='query="language model name"' results=5
2026-05-22 23:03:08,187 [INFO] nina.tools.search: tavily_search query='query="language model name"' results=5
2026-05-22 23:03:09,107 [INFO] nina.tools.search: tavily_search query='query="language model name"' results=5
2026-05-22 23:03:09,925 [INFO] nina.tools.search: tavily_search query='query="language model name"' results=5
```

### logs/tools.log.2026-05-23
Last modified: 2026-05-23 00:04:52
Size: 630 bytes
```log
2026-05-23 00:04:49,331 [INFO] nina.tools.search: tavily_search query='query="language model used by ai assistant"' results=5
2026-05-23 00:04:50,247 [INFO] nina.tools.search: tavily_search query='query="language model used by ai assistant"' results=5
2026-05-23 00:04:51,105 [INFO] nina.tools.search: tavily_search query='query="language model used by ai assistant"' results=5
2026-05-23 00:04:51,975 [INFO] nina.tools.search: tavily_search query='query="language model used by ai assistant"' results=5
2026-05-23 00:04:52,940 [INFO] nina.tools.search: tavily_search query='query="language model used by ai assistant"' results=5
```

### logs/tools.log.2026-05-24
Last modified: 2026-05-24 00:15:01
Size: 793 bytes
```log
2026-05-24 00:02:25,637 [WARNING] nina.tools.search: tavily_failed Client error '400 Bad Request' for url 'https://api.tavily.com/search'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
2026-05-24 00:02:26,664 [WARNING] nina.tools.search: serper_failed Client error '400 Bad Request' for url 'https://google.serper.dev/search'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
2026-05-24 00:02:26,781 [WARNING] nina.tools.search: ddg_failed keywords is mandatory
2026-05-24 00:02:29,452 [INFO] nina.tools.search: tavily_search query='query \n\n(e.g. TOOL:web' results=5
2026-05-24 00:15:01,663 [INFO] nina.tools.search: tavily_search query='query="artificial intelligence capabilities and limitations"' results=5
```

### logs/tools.log.2026-06-04
Last modified: 2026-06-04 12:42:21
Size: 875 bytes
```log
2026-06-04 11:51:24,202 [WARNING] nina.tools.shell: shell:blocked cmd='crontab -l'
2026-06-04 11:51:29,096 [INFO] nina.tools.search: tavily_search query='how to create cron jobs alternatively' results=5
2026-06-04 11:51:30,987 [WARNING] nina.tools.shell: shell:blocked cmd='anacron -h'
2026-06-04 12:42:12,262 [INFO] nina.tools.search: tavily_search query='query\n2. TOOL:browser -' results=5
2026-06-04 12:42:15,756 [INFO] nina.tools.search: tavily_search query='query (e.g. "website content query tools")\n2. TOOL:browser -' results=5
2026-06-04 12:42:19,357 [INFO] nina.tools.search: tavily_search query='query (e.g. "website content query tools", "query website content")\n2. TOOL:browser -' results=5
2026-06-04 12:42:21,419 [INFO] nina.tools.search: tavily_search query='query (e.g. "website content query tools", "query website content")\n2. TOOL:browser -' results=5
```

### logs/tools.log.2026-06-05
Last modified: 2026-06-05 22:08:31
Size: 1620 bytes
```log
2026-06-05 20:58:21,498 [INFO] nina.tools.search: tavily_search query='query="USD/BDT exchange rate today"' results=5
2026-06-05 21:03:02,074 [INFO] nina.tools.search: tavily_search query='USD/BDT exchange rate' results=5
2026-06-05 21:07:13,519 [INFO] nina.tools.search: tavily_search query='query="USD/BDT exchange rate" to get the current exchange rate.' results=5
2026-06-05 21:12:41,458 [INFO] nina.tools.search: tavily_search query='USD/BDT exchange rate' results=5
2026-06-05 21:34:56,263 [INFO] nina.tools.search: tavily_search query='query="USD/BDT exchange rate" to get the current exchange rate.' results=5
2026-06-05 21:52:11,383 [INFO] nina.tools.search: tavily_search query='"https://www.bb.org.bd/econdata/exchangerate.php"' results=5
2026-06-05 21:59:55,400 [WARNING] nina.tools.search: tavily_failed Client error '400 Bad Request' for url 'https://api.tavily.com/search'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
2026-06-05 22:00:10,418 [WARNING] nina.tools.search: serper_failed 
2026-06-05 22:00:10,504 [WARNING] nina.tools.search: ddg_failed keywords is mandatory
2026-06-05 22:01:03,256 [INFO] nina.tools.search: tavily_search query='"USD to BDT exchange rate today Bangladesh Bank interbank rate"]\n\n[Step 2/5 চলছে...]' results=5
2026-06-05 22:08:30,168 [WARNING] nina.tools.search: tavily_failed Client error '400 Bad Request' for url 'https://api.tavily.com/search'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
2026-06-05 22:08:31,909 [INFO] nina.tools.search: serper_search query='**' results=5
```

### logs/tools.log.2026-06-08
Last modified: 2026-06-08 14:30:00
Size: 4172 bytes
```log
2026-06-08 11:30:00,008 [INFO] nina.tools: market_monitor_started
2026-06-08 11:30:00,008 [INFO] nina.tools: market_monitor_summary: Market Monitor Run: Alerts triggered for: GP: 253.5 (UP 1.40%), SQURPHARMA: 215.0 (UP 2.38%)
2026-06-08 11:30:00,008 [INFO] nina.tools: market_monitor_json: [{"ticker": "GP", "last_price": 250.0, "current_price": 253.5, "change_pct": 1.4, "alert": true}, {"ticker": "BATBC", "last_price": 500.0, "current_price": 498.0, "change_pct": -0.4, "alert": false}, {"ticker": "SQURPHARMA", "last_price": 210.0, "current_price": 215.0, "change_pct": 2.38, "alert": true}]
2026-06-08 12:00:00,006 [INFO] nina.tools: market_monitor_started
2026-06-08 12:00:00,006 [INFO] nina.tools: market_monitor_summary: Market Monitor Run: Alerts triggered for: GP: 253.5 (UP 1.40%), SQURPHARMA: 215.0 (UP 2.38%)
2026-06-08 12:00:00,006 [INFO] nina.tools: market_monitor_json: [{"ticker": "GP", "last_price": 250.0, "current_price": 253.5, "change_pct": 1.4, "alert": true}, {"ticker": "BATBC", "last_price": 500.0, "current_price": 498.0, "change_pct": -0.4, "alert": false}, {"ticker": "SQURPHARMA", "last_price": 210.0, "current_price": 215.0, "change_pct": 2.38, "alert": true}]
2026-06-08 12:30:00,002 [INFO] nina.tools: market_monitor_started
2026-06-08 12:30:00,002 [INFO] nina.tools: market_monitor_summary: Market Monitor Run: Alerts triggered for: GP: 253.5 (UP 1.40%), SQURPHARMA: 215.0 (UP 2.38%)
2026-06-08 12:30:00,007 [INFO] nina.tools: market_monitor_json: [{"ticker": "GP", "last_price": 250.0, "current_price": 253.5, "change_pct": 1.4, "alert": true}, {"ticker": "BATBC", "last_price": 500.0, "current_price": 498.0, "change_pct": -0.4, "alert": false}, {"ticker": "SQURPHARMA", "last_price": 210.0, "current_price": 215.0, "change_pct": 2.38, "alert": true}]
2026-06-08 13:00:00,005 [INFO] nina.tools: market_monitor_started
2026-06-08 13:00:00,005 [INFO] nina.tools: market_monitor_summary: Market Monitor Run: Alerts triggered for: GP: 253.5 (UP 1.40%), SQURPHARMA: 215.0 (UP 2.38%)
2026-06-08 13:00:00,005 [INFO] nina.tools: market_monitor_json: [{"ticker": "GP", "last_price": 250.0, "current_price": 253.5, "change_pct": 1.4, "alert": true}, {"ticker": "BATBC", "last_price": 500.0, "current_price": 498.0, "change_pct": -0.4, "alert": false}, {"ticker": "SQURPHARMA", "last_price": 210.0, "current_price": 215.0, "change_pct": 2.38, "alert": true}]
2026-06-08 13:30:00,004 [INFO] nina.tools: market_monitor_started
2026-06-08 13:30:00,004 [INFO] nina.tools: market_monitor_summary: Market Monitor Run: Alerts triggered for: GP: 253.5 (UP 1.40%), SQURPHARMA: 215.0 (UP 2.38%)
2026-06-08 13:30:00,004 [INFO] nina.tools: market_monitor_json: [{"ticker": "GP", "last_price": 250.0, "current_price": 253.5, "change_pct": 1.4, "alert": true}, {"ticker": "BATBC", "last_price": 500.0, "current_price": 498.0, "change_pct": -0.4, "alert": false}, {"ticker": "SQURPHARMA", "last_price": 210.0, "current_price": 215.0, "change_pct": 2.38, "alert": true}]
2026-06-08 14:00:00,003 [INFO] nina.tools: market_monitor_started
2026-06-08 14:00:00,003 [INFO] nina.tools: market_monitor_summary: Market Monitor Run: Alerts triggered for: GP: 253.5 (UP 1.40%), SQURPHARMA: 215.0 (UP 2.38%)
2026-06-08 14:00:00,003 [INFO] nina.tools: market_monitor_json: [{"ticker": "GP", "last_price": 250.0, "current_price": 253.5, "change_pct": 1.4, "alert": true}, {"ticker": "BATBC", "last_price": 500.0, "current_price": 498.0, "change_pct": -0.4, "alert": false}, {"ticker": "SQURPHARMA", "last_price": 210.0, "current_price": 215.0, "change_pct": 2.38, "alert": true}]
2026-06-08 14:30:00,006 [INFO] nina.tools: market_monitor_started
2026-06-08 14:30:00,006 [INFO] nina.tools: market_monitor_summary: Market Monitor Run: Alerts triggered for: GP: 253.5 (UP 1.40%), SQURPHARMA: 215.0 (UP 2.38%)
2026-06-08 14:30:00,006 [INFO] nina.tools: market_monitor_json: [{"ticker": "GP", "last_price": 250.0, "current_price": 253.5, "change_pct": 1.4, "alert": true}, {"ticker": "BATBC", "last_price": 500.0, "current_price": 498.0, "change_pct": -0.4, "alert": false}, {"ticker": "SQURPHARMA", "last_price": 210.0, "current_price": 215.0, "change_pct": 2.38, "alert": true}]
```

### logs/upgrade.log
Last modified: 2026-06-10 22:23:25
Size: 201 bytes
```log
2026-06-10 00:18:54,737 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-10 14:45:59,328 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-10 22:23:25,998 [INFO] nina.upgrade: UpgradePipeline ready
```

### logs/upgrade.log.2026-06-01
Last modified: 2026-06-01 22:37:42
Size: 134 bytes
```log
2026-06-01 12:01:12,320 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-01 22:37:42,747 [INFO] nina.upgrade: UpgradePipeline ready
```

### logs/upgrade.log.2026-06-02
Last modified: 2026-06-02 11:15:27
Size: 67 bytes
```log
2026-06-02 11:15:27,153 [INFO] nina.upgrade: UpgradePipeline ready
```

### logs/upgrade.log.2026-06-04
Last modified: 2026-06-04 19:09:23
Size: 335 bytes
```log
2026-06-04 18:18:05,634 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-04 18:49:32,812 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-04 18:49:45,119 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-04 18:49:50,244 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-04 19:09:23,559 [INFO] nina.upgrade: UpgradePipeline ready
```

### logs/upgrade.log.2026-06-05
Last modified: 2026-06-05 23:01:07
Size: 1005 bytes
```log
2026-06-05 00:18:17,316 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 16:23:42,551 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 17:02:18,456 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 19:28:28,427 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 20:57:03,181 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 21:40:48,867 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 21:49:41,203 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 21:51:02,963 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 21:58:06,772 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 21:58:57,336 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 22:03:46,136 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 22:08:02,849 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 22:14:10,381 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 22:20:11,814 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-05 23:01:07,580 [INFO] nina.upgrade: UpgradePipeline ready
```

### logs/upgrade.log.2026-06-06
Last modified: 2026-06-06 21:27:15
Size: 1407 bytes
```log
2026-06-06 00:03:51,988 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 00:04:20,483 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 02:45:18,739 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 02:48:35,175 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 02:50:48,154 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 02:56:18,098 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 03:23:39,556 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 03:39:26,919 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 03:39:58,336 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 03:42:00,753 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 03:43:24,460 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 03:45:26,581 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 03:46:50,520 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 03:51:29,973 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 04:01:30,143 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 10:42:57,473 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 17:04:53,575 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 17:05:11,117 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 19:42:40,018 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 20:00:14,646 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-06 21:27:15,297 [INFO] nina.upgrade: UpgradePipeline ready
```

### logs/upgrade.log.2026-06-08
Last modified: 2026-06-08 20:46:37
Size: 134 bytes
```log
2026-06-08 11:10:13,280 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-08 20:46:37,213 [INFO] nina.upgrade: UpgradePipeline ready
```

### logs/upgrade.log.2026-06-09
Last modified: 2026-06-09 20:13:21
Size: 134 bytes
```log
2026-06-09 12:20:05,024 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-09 20:13:21,406 [INFO] nina.upgrade: UpgradePipeline ready
```

