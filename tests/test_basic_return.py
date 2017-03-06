import sys
import os
sys.path.append(os.path.abspath("scripts/rabbitmq") )
from api import *

import io
import pytest

def test_output_default_help_message(capsys):
    with pytest.raises(SystemExit):
        main()
    out, err = capsys.readouterr()
    assert "At least one check should be specified" in err

debugoutput = ""
def test_queue_check(capsys, monkeypatch):
    current_args = sys.argv
    sys.argv = ["prog", "--check","list_queues"]
    def mockloggingconfig(filename, level, format):
        assert filename == "/var/log/zabbix/rabbitmq_zabbix.log"
    def mockdebug(somestring):
        global debugoutput 
        debugoutput = debugoutput + somestring + "####"
    monkeypatch.setattr(logging, "basicConfig", mockloggingconfig)
    monkeypatch.setattr(logging, "debug", mockdebug)
    monkeypatch.setattr(logging, "info", mockdebug)

    with pytest.raises(Exception):
        main()
    out, err = capsys.readouterr()
    assert "Started trying to process data" in debugoutput
    assert "Issue a rabbit" in debugoutput



