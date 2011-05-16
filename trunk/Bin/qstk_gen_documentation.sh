EPYDOC_PATH=epydoc-3.0.1
HTML_DOCS_PATH=$QS/Docs/html
PDF_DOCS_PATH=$QS/Docs/pdf
OLD_PY_PATH=$PYTHONPATH
export PYTHONPATH=":$QS/${EPYDOC_PATH}"$PYTHONPATH
rm ${HTML_DOCS_PATH}/*
rm ${PDF_DOCS_PATH}/*
svn del --force ${HTML_DOCS_PATH}
svn del --force ${PDF_DOCS_PATH}

mkdir ${HTML_DOCS_PATH}
mkdir ${PDF_DOCS_PATH}

$QS/${EPYDOC_PATH}/scripts/epydoc --html $QS -o ${HTML_DOCS_PATH} --name QSTK
$QS/${EPYDOC_PATH}/scripts/epydoc --pdf $QS -o ${PDF_DOCS_PATH} --name QSTK
export PYTHONPATH=${OLD_PY_PATH}
svn add ${HTML_DOCS_PATH}
svn add ${PDF_DOCS_PATH}
echo "NOTE: New documentation is still not committed to repository. Please use svn commit do commit to repository."