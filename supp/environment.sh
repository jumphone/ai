PYTHON_TGZ_PATH=/home/toolkit/tools/Python3.12.13/
PYTHON_BIN_PATH=/home/toolkit/local_py312/bin/

:<<!
${PYTHON_TGZ_PATH}configure --prefix=/home/toolkit/local_py312/ \
            --with-openssl=/opt/openssl \
            --with-openssl-rpath=auto
${PYTHON_BIN_PATH}pip3 download -r docs/requirements.txt -d /home/toolkit/tools/ai_local_src/pip_packages
${PYTHON_BIN_PATH}pip3 install -r docs/requirements.txt --no-index --find-links=/home/toolkit/tools/ai_local_src/pip_packages 
${PYTHON_BIN_PATH}pip3 install -r docs/requirements.txt
!

${PYTHON_BIN_PATH}pip3 list > docs/pypack.md
${PYTHON_BIN_PATH}pip3 freeze > docs/requirements.txt
