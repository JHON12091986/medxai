from append_log import append_to_log
from append_lock import update_lock_file

def test_append_log_creates_file(nina_tmp_dir, monkeypatch):
    test_log = nina_tmp_dir / "nina_update_log.md"
    monkeypatch.setattr("append_log.LOG_FILE", str(test_log))
    test_log.write_text("Dummy content")

    append_to_log()

    assert test_log.exists()
    content = test_log.read_text()
    assert "Implement F-04 Expenditure Tracker" in content

def test_append_log_appends_not_overwrites(nina_tmp_dir, monkeypatch):
    test_log = nina_tmp_dir / "nina_update_log.md"
    monkeypatch.setattr("append_log.LOG_FILE", str(test_log))
    test_log.write_text("Dummy content\n")

    append_to_log()
    append_to_log()

    content = test_log.read_text()
    assert content.count("Implement F-04 Expenditure Tracker") == 2

def test_append_lock_creates_lockfile(nina_tmp_dir, monkeypatch):
    test_lock = nina_tmp_dir / "jules_lock.txt"
    monkeypatch.setattr("append_lock.LOCK_FILE", str(test_lock))
    test_lock.write_text("LOCKED_FILES=\n")

    update_lock_file()

    assert test_lock.exists()
    content = test_lock.read_text()
    assert "tools/finance.py" in content

def test_append_lock_idempotent(nina_tmp_dir, monkeypatch):
    test_lock = nina_tmp_dir / "jules_lock.txt"
    monkeypatch.setattr("append_lock.LOCK_FILE", str(test_lock))
    test_lock.write_text("LOCKED_FILES=\n")

    update_lock_file()
    content1 = test_lock.read_text()

    update_lock_file()
    content2 = test_lock.read_text()

    assert content1 == content2
