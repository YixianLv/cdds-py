"""
    This module contains the internal wiring for the Cyclone DDS Python API.
    In normal operation you shouldn't need to call or reference any of the functionality offered here.
"""

import os
import uuid
import inspect
import platform
import ctypes as ct


def load_cyclone() -> ct.CDLL:
    """
        Internal method to load the Cyclone Dynamic Library.
        Handles platform specific naming/configuration.
    """
    load_method = ""
    load_path = ""

    if 'CDDS_NO_IMPORT_LIBS' in os.environ:
        return None

    if 'ddsc' in os.environ:
        # library was directly specified in environment variables
        load_method = 'env'
        load_path = [os.environ['ddsc']]
    elif "CYCLONEDDS_HOME" in os.environ and platform.system() == "Linux":
        load_method = 'home'
        load_path = [os.path.join(os.environ["CYCLONEDDS_HOME"], "lib", "libddsc.so")]
    elif "CYCLONEDDS_HOME" in os.environ and platform.system() == "Darwin":
        load_method = 'home'
        load_path = [os.path.join(os.environ["CYCLONEDDS_HOME"], "lib", "libddsc.dylib")]
    elif "CYCLONEDDS_HOME" in os.environ and platform.system() == "Windows":
        load_method = 'home'
        load_path = [os.path.join(os.environ["CYCLONEDDS_HOME"], "bin", "ddsc.dll")]
    elif platform.system() == "Linux":
        load_method = "guess"
        load_path = [os.path.join(p, "libddsc.so") for p in [
            "", "/usr/lib/", "/usr/local/lib/", "/usr/lib64/", "/lib/", "/lib64/"]
        ]
    elif platform.system() == "Darwin":
        load_method = "guess"
        load_path = [os.path.join(p, "libddsc.dylib") for p in [
            "", "/usr/lib/", "/usr/local/lib/", "/usr/lib64/", "/lib/", "/lib64/"]
        ]
    else:
        load_method = "guess"
        load_path = ["libddsc.so", "ddsc.dll", "libddsc.dylib"]

    lib = None
    for path in load_path:
        try:
            lib = ct.CDLL(path)
        except OSError:
            continue
        if lib:
            break

    if not lib:
        raise Exception(f"Failed to load CycloneDDS with method {load_method} from path(s): {', '.join(load_path)}.")

    return lib


def c_call(cname):
    """
        Decorator. Convert a function into call into the class associated dll.
    """

    class DllCall:
        def __init__(self, function):
            self.function = function

        # This gets called when the class is finalized
        def __set_name__(self, cls, name):
            if 'CDDS_NO_IMPORT_LIBS' in os.environ:
                return

            s = inspect.signature(self.function)

            # Set c function types based on python type annotations
            cfunc = getattr(cls._dll_handle, cname)

            # Note: in python 3.10 we get NoneType for voids instead of None
            # This confuses ctypes a lot, so we explicitly test for it
            # We also add the ignore for the error that flake8 generates
            cfunc.restype = s.return_annotation if s.return_annotation != type(None) else None  # noqa: E721

            # Note: ignoring the 'self' argument
            cfunc.argtypes = [p.annotation for i, p in enumerate(s.parameters.values()) if i > 0]

            # Need to rebuild this function to ignore the 'self' attribute
            def final_func(self_, *args):
                return cfunc(*args)

            # replace class named method with c call
            setattr(cls, name, final_func)

    return DllCall


def c_callable(return_type, argument_types) -> ct.CFUNCTYPE:
    """
        Decorator. Make a C function type based on python type annotations.
    """
    return ct.CFUNCTYPE(return_type, *argument_types)


class DDS:
    """
        Common class for all DDS related classes. This class enables the c_call magic.
    """
    _dll_handle = load_cyclone()

    def __init__(self, reference: int) -> None:
        self._ref = reference


class dds_c_t:
    entity = ct.c_int32
    time = ct.c_int64
    duration = ct.c_int64
    instance_handle = ct.c_int64
    domainid = ct.c_uint32
    sample_state = ct.c_int
    view_state = ct.c_int
    instance_state = ct.c_int
    reliability = ct.c_int
    durability = ct.c_int
    history = ct.c_int
    presentation_access_scope = ct.c_int
    ingnorelocal = ct.c_int
    ownership = ct.c_int
    liveliness = ct.c_int
    destination_order = ct.c_int
    qos_p = ct.c_void_p
    attach = ct.c_void_p
    listener_p = ct.c_void_p
    topic_descriptor_p = ct.c_void_p
    returnv = ct.c_int32

    class inconsistent_topic_status(ct.Structure):
        _fields_ = [('total_count', ct.c_uint32),
                    ('total_count_change', ct.c_int32)]

    class liveliness_lost_status(ct.Structure):
        _fields_ = [('total_count', ct.c_uint32),
                    ('total_count_change', ct.c_int32)]

    class liveliness_changed_status(ct.Structure):
        _fields_ = [('alive_count', ct.c_uint32),
                    ('not_alive_count', ct.c_uint32),
                    ('alive_count_change', ct.c_int32),
                    ('not_alive_count_change', ct.c_int32),
                    ('last_publication_handle', ct.c_int64)]

    class offered_deadline_missed_status(ct.Structure):
        _fields_ = [('total_count', ct.c_uint32),
                    ('total_count_change', ct.c_int32),
                    ('last_instance_handle', ct.c_int64)]

    class offered_incompatible_qos_status(ct.Structure):
        _fields_ = [('total_count', ct.c_uint32),
                    ('total_count_change', ct.c_int32),
                    ('last_policy_id', ct.c_uint32)]

    class sample_lost_status(ct.Structure):
        _fields_ = [('total_count', ct.c_uint32),
                    ('total_count_change', ct.c_int32)]

    class sample_rejected_status(ct.Structure):
        _fields_ = [('total_count', ct.c_uint32),
                    ('total_count_change', ct.c_int32),
                    ('last_reason', ct.c_int),
                    ('last_instance_handle', ct.c_int64)]

    class requested_deadline_missed_status(ct.Structure):
        _fields_ = [('total_count', ct.c_uint32),
                    ('total_count_change', ct.c_int32),
                    ('last_instance_handle', ct.c_int64)]

    class requested_incompatible_qos_status(ct.Structure):
        _fields_ = [('total_count', ct.c_uint32),
                    ('total_count_change', ct.c_int32),
                    ('last_policy_id', ct.c_uint32)]

    class publication_matched_status(ct.Structure):
        _fields_ = [('total_count', ct.c_uint32),
                    ('total_count_change', ct.c_int32),
                    ('current_count', ct.c_uint32),
                    ('current_count_change', ct.c_int32),
                    ('last_subscription_handle', ct.c_int64)]

    class subscription_matched_status(ct.Structure):
        _fields_ = [('total_count', ct.c_uint32),
                    ('total_count_change', ct.c_int32),
                    ('current_count', ct.c_uint32),
                    ('current_count_change', ct.c_int32),
                    ('last_publication_handle', ct.c_int64)]

    class guid(ct.Structure):
        _fields_ = [('v', ct.c_uint8 * 16)]

        def as_python_guid(self) -> uuid.UUID:
            return uuid.UUID(bytes=bytes(self.v))

    class sample_info(ct.Structure):
        _fields_ = [
            ('sample_state', ct.c_uint),
            ('view_state', ct.c_uint),
            ('instance_state', ct.c_uint),
            ('valid_data', ct.c_bool),
            ('source_timestamp', ct.c_int64),
            ('instance_handle', ct.c_uint64),
            ('pubblication_handle', ct.c_uint64),
            ('disposed_generation_count', ct.c_uint32),
            ('no_writer_generation_count', ct.c_uint32),
            ('sample_rank', ct.c_uint32),
            ('generation_rank', ct.c_uint32),
            ('absolute_generation_rank', ct.c_uint32)
        ]
