# wbmtranslator

wbmtranslator is the translation assistant for [Webmin](http://www.webmin.com) / [Usermin](http://www.webmin.com/usermin.html) modules. It allows Webmin / Usermin translators to have a global view of current translations for all registered modules and themes, including the web interface and configuration screens. They can accurately track changes, create or update translations, send them to the Webmin team, and more.

## Installation

### From a wbm archive:

Open the Webmin modules manager and upload the wbmtranslator file.

### From the Git repository:

1. Rename your local Git repository (optional):
```bash
mv wbmtranslator/ translator/
```
2. Build a gzipped tarball archive:
```bash
tar zcvf wbmtranslator.wbm.gz translator/
```
3. Open the Webmin modules manager and upload your brand new wbmtranslator file.

## Perl dependencies

You need at least the following Perl modules in order to run wbmtranslator:

- Date::Manip
- Digest::MD5
- Encode
- File::Basename
- File::Copy
- File::Path
- HTML::Entities
- JSON
- LWP::UserAgent
- MIME::Lite
- POSIX

Depending on the software installed on your system and your wbmtranslator configuration options, you may also need the following modules:

- Authen::NTLM
- Digest::HMAC_MD5
- Mail::Sender

All those modules can be loaded from CPAN.

As root you can try:

```bash
# perl -MCPAN -e shell
CPAN Shell> install module1 module2 ...
```

## License
GPL
