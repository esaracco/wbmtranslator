<p align="center"><img src="http://wbmtranslator.esaracco.fr/images/wbmtranslator.png"/></p>

# wbmtranslator

 [Project homepage](http://wbmtranslator.esaracco.fr)

wbmtranslator is the translation assistant for [Webmin](http://www.webmin.com) / [Usermin](http://www.webmin.com/usermin.html) modules. It allows Webmin / Usermin translators to have a global view of current translations for all registered modules and themes, including the web interface and configuration screens. They can accurately track changes, create or update translations, send them to the Webmin team, and more.

## Installation
### From a wbm archive :
Open the Webmin modules manager and upload the wbmclamav file.
### From the Git repository :

1. Change the owner and permissions of the entire tree :
```bash
chmod -R 755 translator/
chown -R root:bin translator/
```
2. Build a gzipped tarball archive :
```bash
tar zcvf wbmtranslator.wbm.gz translator/
```
3. Open the Webmin modules manager and upload your brand new wbmtranslator file.


## License
GPL
