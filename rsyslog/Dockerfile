FROM rsyslog/syslog_appliance_alpine

COPY rsyslog.d /etc/rsyslog.d/
COPY rsyslog.conf /etc/rsyslog.conf

RUN apk add rsyslog-hiredis