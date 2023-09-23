#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <windows.h>

void utf8ToGB2312(char * utf8,char* ansi)
{
    wchar_t wstr[2048];
    memset(wstr, 0, 2048);
    MultiByteToWideChar(CP_UTF8, 0, utf8, -1, wstr, 2048);
    char strFilename[2048]="";
    WideCharToMultiByte(CP_ACP, 0, wstr, -1, ansi, 2048, NULL, NULL);
}

static PyObject *exec(PyObject *self, PyObject *args)
{
    const char *operation;
    const char *filename;
    const char *param;
    int  show = 0;
    int sts=0;

    if (!PyArg_ParseTuple(args, "sssl", &operation,&filename,&param,&show))
        return NULL;

    char ansi_name[2048];
    char ansi_param[2048];
    utf8ToGB2312(filename,ansi_name);
    utf8ToGB2312(param,ansi_param);

    ShellExecuteA (NULL,operation,ansi_name,ansi_param,NULL,show);
    
    return PyLong_FromLong(sts);
}

static PyMethodDef shellexecuteMethods[] = {
    {"exec",  exec, METH_VARARGS,"Execute a shell command."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


static struct PyModuleDef shellexecutemodule = {
    PyModuleDef_HEAD_INIT,
    "shellexecute",   /* name of module */
    "", /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    shellexecuteMethods
};


PyMODINIT_FUNC PyInit_shellexecute(void)
{
    PyObject *m;
    m = PyModule_Create(&shellexecutemodule);
    if (m == NULL)
        return NULL;
    PyObject * SpamError = PyErr_NewException("shellexecute.error", NULL, NULL);
    Py_XINCREF(SpamError);
    if (PyModule_AddObject(m, "error", SpamError) < 0) {
        Py_XDECREF(SpamError);
        Py_CLEAR(SpamError);
        Py_DECREF(m);
        return NULL;
    }
    return m;
}