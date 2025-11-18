/*
 * audio_writer.c - High-performance audio writer C extension for Python
 * 
 * This module provides a fast C implementation for converting float32 audio
 * data to 24-bit PCM and writing to multiple WAV files simultaneously.
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>
#include <stdio.h>
#include <stdint.h>

/* Convert float32 sample to 24-bit signed integer bytes */
static inline void float_to_24bit(float sample, uint8_t *output) {
    /* Clamp to valid range [-1.0, 1.0] */
    if (sample > 1.0f) sample = 1.0f;
    if (sample < -1.0f) sample = -1.0f;
    
    /* Convert to 24-bit integer range */
    int32_t sample_24 = (int32_t)(sample * 8388607.0f);  /* 2^23 - 1 */
    
    /* Write as 3 bytes (little endian) */
    output[0] = (uint8_t)(sample_24 & 0xFF);
    output[1] = (uint8_t)((sample_24 >> 8) & 0xFF);
    output[2] = (uint8_t)((sample_24 >> 16) & 0xFF);
}

/*
 * write_multichannel_24bit - Convert and write multi-channel audio data
 * 
 * Args:
 *   audio_data: NumPy array of float32, shape (frames, total_channels)
 *   channel_indices: List of channel indices to extract
 *   file_objects: List of Python file objects (opened WAV files)
 * 
 * Returns:
 *   Number of frames written
 */
static PyObject* write_multichannel_24bit(PyObject *self, PyObject *args) {
    PyArrayObject *audio_array;
    PyObject *channel_list;
    PyObject *file_list;
    
    /* Parse arguments */
    if (!PyArg_ParseTuple(args, "O!OO", 
                          &PyArray_Type, &audio_array,
                          &channel_list, 
                          &file_list)) {
        return NULL;
    }
    
    /* Verify audio_array is a 2D float32 array */
    if (PyArray_NDIM(audio_array) != 2) {
        PyErr_SetString(PyExc_ValueError, "audio_data must be 2D array");
        return NULL;
    }
    
    if (PyArray_TYPE(audio_array) != NPY_FLOAT32) {
        PyErr_SetString(PyExc_TypeError, "audio_data must be float32");
        return NULL;
    }
    
    /* Verify lists */
    if (!PyList_Check(channel_list)) {
        PyErr_SetString(PyExc_TypeError, "channel_indices must be a list");
        return NULL;
    }
    
    if (!PyList_Check(file_list)) {
        PyErr_SetString(PyExc_TypeError, "file_objects must be a list");
        return NULL;
    }
    
    /* Get dimensions */
    npy_intp *dims = PyArray_DIMS(audio_array);
    npy_intp num_frames = dims[0];
    npy_intp total_channels = dims[1];
    
    Py_ssize_t num_channels = PyList_Size(channel_list);
    
    if (num_channels != PyList_Size(file_list)) {
        PyErr_SetString(PyExc_ValueError, 
                       "channel_indices and file_objects must have same length");
        return NULL;
    }
    
    /* Get pointer to audio data */
    float *audio_data = (float *)PyArray_DATA(audio_array);
    
    /* Allocate buffer for 24-bit samples (3 bytes per sample) */
    uint8_t *buffer_24bit = (uint8_t *)malloc(num_frames * 3);
    if (!buffer_24bit) {
        PyErr_NoMemory();
        return NULL;
    }
    
    /* Process each channel */
    for (Py_ssize_t ch_idx = 0; ch_idx < num_channels; ch_idx++) {
        /* Get channel index */
        PyObject *ch_obj = PyList_GetItem(channel_list, ch_idx);
        long channel = PyLong_AsLong(ch_obj);
        
        if (channel < 0 || channel >= total_channels) {
            free(buffer_24bit);
            PyErr_Format(PyExc_ValueError, 
                        "Invalid channel index %ld (total channels: %ld)", 
                        channel, total_channels);
            return NULL;
        }
        
        /* Convert channel data to 24-bit */
        for (npy_intp frame = 0; frame < num_frames; frame++) {
            float sample = audio_data[frame * total_channels + channel];
            float_to_24bit(sample, &buffer_24bit[frame * 3]);
        }
        
        /* Get file object */
        PyObject *file_obj = PyList_GetItem(file_list, ch_idx);
        
        /* Create bytes object from buffer */
        PyObject *bytes_obj = PyBytes_FromStringAndSize(
            (char *)buffer_24bit, 
            num_frames * 3
        );
        
        if (!bytes_obj) {
            free(buffer_24bit);
            return NULL;
        }
        
        /* Call file.write() method */
        PyObject *write_result = PyObject_CallMethod(file_obj, "write", "O", bytes_obj);
        Py_DECREF(bytes_obj);
        
        if (!write_result) {
            free(buffer_24bit);
            return NULL;
        }
        Py_DECREF(write_result);
    }
    
    free(buffer_24bit);
    
    /* Return number of frames written */
    return PyLong_FromLong((long)num_frames);
}

/*
 * write_multichannel_24bit_int32 - Convert and write from int32 input
 * 
 * This version accepts int32 input (as already scaled by Python code)
 * and converts to 24-bit format.
 * 
 * Args:
 *   audio_data: NumPy array of int32, shape (frames, total_channels)
 *   channel_indices: List of channel indices to extract
 *   file_objects: List of Python file objects (opened WAV files)
 * 
 * Returns:
 *   Number of frames written
 */
static PyObject* write_multichannel_24bit_int32(PyObject *self, PyObject *args) {
    PyArrayObject *audio_array;
    PyObject *channel_list;
    PyObject *file_list;
    
    /* Parse arguments */
    if (!PyArg_ParseTuple(args, "O!OO", 
                          &PyArray_Type, &audio_array,
                          &channel_list, 
                          &file_list)) {
        return NULL;
    }
    
    /* Verify audio_array is a 2D int32 array */
    if (PyArray_NDIM(audio_array) != 2) {
        PyErr_SetString(PyExc_ValueError, "audio_data must be 2D array");
        return NULL;
    }
    
    if (PyArray_TYPE(audio_array) != NPY_INT32) {
        PyErr_SetString(PyExc_TypeError, "audio_data must be int32");
        return NULL;
    }
    
    /* Verify lists */
    if (!PyList_Check(channel_list)) {
        PyErr_SetString(PyExc_TypeError, "channel_indices must be a list");
        return NULL;
    }
    
    if (!PyList_Check(file_list)) {
        PyErr_SetString(PyExc_TypeError, "file_objects must be a list");
        return NULL;
    }
    
    /* Get dimensions */
    npy_intp *dims = PyArray_DIMS(audio_array);
    npy_intp num_frames = dims[0];
    npy_intp total_channels = dims[1];
    
    Py_ssize_t num_channels = PyList_Size(channel_list);
    
    if (num_channels != PyList_Size(file_list)) {
        PyErr_SetString(PyExc_ValueError, 
                       "channel_indices and file_objects must have same length");
        return NULL;
    }
    
    /* Get pointer to audio data */
    int32_t *audio_data = (int32_t *)PyArray_DATA(audio_array);
    
    /* Allocate buffer for 24-bit samples (3 bytes per sample) */
    uint8_t *buffer_24bit = (uint8_t *)malloc(num_frames * 3);
    if (!buffer_24bit) {
        PyErr_NoMemory();
        return NULL;
    }
    
    /* Process each channel */
    for (Py_ssize_t ch_idx = 0; ch_idx < num_channels; ch_idx++) {
        /* Get channel index */
        PyObject *ch_obj = PyList_GetItem(channel_list, ch_idx);
        long channel = PyLong_AsLong(ch_obj);
        
        if (channel < 0 || channel >= total_channels) {
            free(buffer_24bit);
            PyErr_Format(PyExc_ValueError, 
                        "Invalid channel index %ld (total channels: %ld)", 
                        channel, total_channels);
            return NULL;
        }
        
        /* Convert channel data to 24-bit */
        for (npy_intp frame = 0; frame < num_frames; frame++) {
            int32_t sample_24 = audio_data[frame * total_channels + channel];
            
            /* Clamp to 24-bit range */
            if (sample_24 > 8388607) sample_24 = 8388607;
            if (sample_24 < -8388608) sample_24 = -8388608;
            
            /* Write as 3 bytes (little endian) */
            buffer_24bit[frame * 3 + 0] = (uint8_t)(sample_24 & 0xFF);
            buffer_24bit[frame * 3 + 1] = (uint8_t)((sample_24 >> 8) & 0xFF);
            buffer_24bit[frame * 3 + 2] = (uint8_t)((sample_24 >> 16) & 0xFF);
        }
        
        /* Get file object */
        PyObject *file_obj = PyList_GetItem(file_list, ch_idx);
        
        /* Create bytes object from buffer */
        PyObject *bytes_obj = PyBytes_FromStringAndSize(
            (char *)buffer_24bit, 
            num_frames * 3
        );
        
        if (!bytes_obj) {
            free(buffer_24bit);
            return NULL;
        }
        
        /* Call file.write() method */
        PyObject *write_result = PyObject_CallMethod(file_obj, "write", "O", bytes_obj);
        Py_DECREF(bytes_obj);
        
        if (!write_result) {
            free(buffer_24bit);
            return NULL;
        }
        Py_DECREF(write_result);
    }
    
    free(buffer_24bit);
    
    /* Return number of frames written */
    return PyLong_FromLong((long)num_frames);
}

/* Module method definitions */
static PyMethodDef AudioWriterMethods[] = {
    {"write_multichannel_24bit", write_multichannel_24bit, METH_VARARGS,
     "Write multi-channel float32 audio data as 24-bit PCM to multiple files.\n\n"
     "Args:\n"
     "    audio_data: NumPy array of float32, shape (frames, total_channels)\n"
     "    channel_indices: List of int, channel indices to extract\n"
     "    file_objects: List of file objects (opened WAV files)\n\n"
     "Returns:\n"
     "    int: Number of frames written\n"},
    
    {"write_multichannel_24bit_int32", write_multichannel_24bit_int32, METH_VARARGS,
     "Write multi-channel int32 audio data as 24-bit PCM to multiple files.\n\n"
     "Args:\n"
     "    audio_data: NumPy array of int32, shape (frames, total_channels)\n"
     "    channel_indices: List of int, channel indices to extract\n"
     "    file_objects: List of file objects (opened WAV files)\n\n"
     "Returns:\n"
     "    int: Number of frames written\n"},
    
    {NULL, NULL, 0, NULL}
};

/* Module definition */
static struct PyModuleDef audio_writer_module = {
    PyModuleDef_HEAD_INIT,
    "audio_writer",
    "High-performance multi-channel audio writer for 24-bit WAV files",
    -1,
    AudioWriterMethods
};

/* Module initialization */
PyMODINIT_FUNC PyInit_audio_writer(void) {
    import_array();  /* Initialize NumPy C API */
    return PyModule_Create(&audio_writer_module);
}
