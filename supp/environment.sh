
/home/toolkit/tools/Python3.12.13/configure --prefix=/home/toolkit/local_py312/ \
            --with-openssl=/opt/openssl \
            --with-openssl-rpath=auto


/home/toolkit/local_py312/bin/pip3 download -r docs/requirements.txt -d /home/toolkit/tools/ai_local_src/pip_packages

/home/toolkit/local_py312/bin/pip3 install -r docs/requirements.txt --no-index --find-links=/home/toolkit/tools/ai_local_src/pip_packages 

/home/toolkit/local_py312/bin/pip3 install -r docs/requirements.txt


/home/toolkit/local_py312/bin/pip3 list > docs/pypack.md

/home/toolkit/local_py312/bin/pip3 freeze > docs/requirements.txt
