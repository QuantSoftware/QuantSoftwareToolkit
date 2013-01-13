/*
 * nagint.c
 *
 * This file implements the python->c interface for the QSTK
 * This must be compiled as nagInterface.so which includes the NAG .a
 *
 *  Created on: Aug 22, 2011
 *      Author: John Cornwell
 */

/* Should be before any other includes */
#include <python2.7/Python.h>

#include <stdio.h>

#include <ndarrayobject.h>

#include <nag.h>
#include <nag_stdlib.h>
#include <nag_string.h>
#include <nage04.h>

static PyObject * optPort(PyObject *self, PyObject *args);

/* List of all method aruments in this module */
static PyMethodDef NagintMethods[] =
{
    {"optPort", optPort, METH_VARARGS, "Calculate optimal portfolio for given ROR."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

/* Called by python when the module is loaded */
PyMODINIT_FUNC initnagint(void)
{
    (void) Py_InitModule("nagint", NagintMethods);

    /* Must be called to import numpy arrays as arguments */
    import_array();
}

/* Frees intermediate array objects used */
_freeMem( PyObject** pObjs, PyArrayObject** pArrays, int lNum )
{
    int i = 0;
    for( i = 0; i < lNum; i++ )
    {	
	Py_XDECREF( pObjs[i] );
	PyArray_XDECREF( pArrays[i] );
    }

}

/* Function which calculates the optimal portfolio allocation for a given ROR */
static PyObject * optPort(PyObject *self, PyObject *args)
{
    const int lNumArray = 5;
    int lNumVar;
    PyObject* pObjs[lNumArray];
    PyArrayObject* pArrays[lNumArray];
    double fReturn;
    int i, j, k;
    int lDebug;

    if( !PyArg_ParseTuple(args, "OOOOOi", &pObjs[0], &pObjs[1], &pObjs[2], &pObjs[3], &pObjs[4], &lDebug ) )
    {
        PyErr_SetString(PyExc_RuntimeError, "Could not parse arguments" );
        return NULL;
    }


    /* Unpack arrays as contiguous double arrays */
    for( i = 0; i < lNumArray; i++ )
    {
        pArrays[i] = (PyArrayObject *) PyArray_ContiguousFromObject(pObjs[i], PyArray_DOUBLE, 0, 0);
        if (pArrays[i] == NULL)
        {
            PyErr_SetString(PyExc_RuntimeError, "Could not unpack array from args");
            return NULL;
        }
    }

#if 0
    /* Print arrays */
    for( i = 0; i < lNumArray; i++ )
    {
        int lM, lN;
        double* pData = (double*)pArrays[i]->data;
        if( pArrays[i]->nd == 1 )
        {
            lM = 1;
            lN = pArrays[i]->dimensions[0];
        }
        else
        {
            lM = pArrays[i]->dimensions[0];
            lN = pArrays[i]->dimensions[1];
        }

        printf("\nArray %i, %ix%i:\n", i, lM, lN);

        for( j = 0; j < lM; j++ )
        {
            for( k = 0; k < lN; k++ )
            {
                printf( "%.02lf ", pData[j * lM + k] );
            }
            printf("\n");
        }
    }
#endif

    lNumVar = pArrays[0]->dimensions[1];
    npy_intp plDims[2];
    plDims[0] = 1;
    plDims[1] = lNumVar + 1;

    /* Create 1 by #var array for return, + 1 for expected variance on the end */
    PyArrayObject* pReturn = (PyArrayObject *)PyArray_SimpleNew( 2, plDims, PyArray_DOUBLE);

    if(pReturn == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Could not create return array" );
        return NULL;
    }


    /* Run through NAG routines */

    /* Print out library info */
    //a00aac();

    Nag_Boolean bPrint = Nag_TRUE;
    NagError tFail;
    Nag_E04_Opt tOpt;

    /* Init options struct and fail struct */
    e04xxc(&tOpt);

    if( lDebug == 0 )
    {
        tOpt.output_level = Nag_NoOutput;
        tOpt.print_gcheck = Nag_FALSE;
        tOpt.print_deriv = Nag_D_NoPrint;
        tOpt.print_level = Nag_NoPrint;
        tOpt.minor_print_level = Nag_NoPrint;
        tOpt.print_iter = -1;
        tOpt.print_80ch = Nag_FALSE;
        tOpt.list = Nag_FALSE;
    }

    INIT_FAIL(tFail);

    /* Set for symmetric quadratic programming */
    tOpt.prob = Nag_QP1;

    /*
     * List of arrays is as follows, (nag label):
     * 0 - Constraints  (a)
     * 1 - Lower bounds  (bl)
     * 2 - Upper bounds  (ub)
     * 3 - Covariance matrix (h)
     * 4 - Initial guess (x)
     */

    double fRetVar;

    double* pConstraints = (double*)pArrays[0]->data;
    double* pBl = (double*)pArrays[1]->data;
    double* pBu = (double*)pArrays[2]->data;
    double* pCov = (double*)pArrays[3]->data;
    double* pInit = (double*)pArrays[4]->data;
    double* pCvec = (double*)malloc( sizeof(double) * lNumVar*1000 );

    /* Allocate some extra variables for the NAG function */
    int lClin = lNumVar+2; /* contraints are # of variables + 2 additional (weights sum to 1, return = desired) */
    int lTda = lNumVar; /* stride of constraints is number of variables */
    int lTdh = lNumVar; /* same for stride of H */

    /* Run algorithm */
    tOpt.inf_bound= 1.0e300;


    e04nfc( lNumVar, 2, pConstraints, lTda, pBl, pBu, pCvec, pCov, lTdh, NULLFN, pInit, &fRetVar, &tOpt, NAGCOMM_NULL, &tFail);
    free(pCvec);

    if( tFail.code != NE_NOERROR )
    {
        PyErr_SetString(PyExc_RuntimeError, "Could not run nag function");
        printf("%s\n",tFail.message);
        e04xzc(&tOpt, "all", &tFail);
        _freeMem( pObjs, pArrays, lNumArray );
        return PyArray_Return(pReturn);
    }

    /* Free memory allocatedby e04nfc to pointers in options */
    e04xzc(&tOpt, "all", &tFail);

    if( tFail.code != NE_NOERROR )
    {
        PyErr_SetString(PyExc_RuntimeError, "Could not free memory");
        _freeMem( pObjs, pArrays, lNumArray );
        return PyArray_Return(pReturn);
    }

    /* Store results, as well as expected return on end */
    memcpy( pReturn->data, pInit, sizeof(double) * lNumVar );
    ((double*)pReturn->data)[lNumVar] = 2*fRetVar;

    _freeMem( pObjs, pArrays, lNumArray );

    return PyArray_Return(pReturn);

}








