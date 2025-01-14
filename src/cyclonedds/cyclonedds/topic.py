"""
 * Copyright(c) 2021 ADLINK Technology Limited and others
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v. 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0, or the Eclipse Distribution License
 * v. 1.0 which is available at
 * http://www.eclipse.org/org/documents/edl-v10.php.
 *
 * SPDX-License-Identifier: EPL-2.0 OR BSD-3-Clause
"""

import ctypes as ct
from typing import Any, AnyStr, TYPE_CHECKING

from .internal import c_call, dds_c_t
from .core import Entity, DDSException
from .qos import _CQos

# The TYPE_CHECKING variable will always evaluate to False, incurring no runtime costs
# But the import here allows your static type checker to resolve fully qualified cyclonedds names
if TYPE_CHECKING:
    import cyclonedds
    def ddspy_topic_create(entity: int, name: str, dtype, qos=None, listener=None):
        pass
else:
    from ddspy import ddspy_topic_create



class Topic(Entity):
    """Representing a Topic"""

    def __init__(
            self,
            domain_participant: 'cyclonedds.domain.DomainParticipant',
            topic_name: AnyStr,
            data_type: Any,
            qos: 'cyclonedds.core.Qos' = None,
            listener: 'cyclonedds.core.Listener' = None):
        self.data_type = data_type
        cqos = _CQos.qos_to_cqos(qos) if qos else None
        super().__init__(
            ddspy_topic_create(
                domain_participant._ref,
                topic_name,
                data_type,
                cqos,
                listener._ref if listener else None
            ),
            listener=listener
        )
        if cqos:
            _CQos.cqos_destroy(cqos)

    def get_name(self, max_size=256):
        name = (ct.c_char * max_size)()
        name_pt = ct.cast(name, ct.c_char_p)
        ret = self._get_name(self._ref, name_pt, max_size)
        if ret < 0:
            raise DDSException(ret, f"Occurred while fetching a topic name for {repr(self)}")
        return bytes(name).split(b'\0', 1)[0].decode("ASCII")

    name = property(get_name, doc="Get topic name")

    def get_type_name(self, max_size=256):
        name = (ct.c_char * max_size)()
        name_pt = ct.cast(name, ct.c_char_p)
        ret = self._get_type_name(self._ref, name_pt, max_size)
        if ret < 0:
            raise DDSException(ret, f"Occurred while fetching a topic type name for {repr(self)}")
        return bytes(name).split(b'\0', 1)[0].decode("ASCII")

    typename = property(get_type_name, doc="Get topic type name")

    @c_call("dds_get_name")
    def _get_name(self, topic: dds_c_t.entity, name: ct.c_char_p, size: ct.c_size_t) -> dds_c_t.returnv:
        pass

    @c_call("dds_get_type_name")
    def _get_type_name(self, topic: dds_c_t.entity, name: ct.c_char_p, size: ct.c_size_t) -> dds_c_t.returnv:
        pass
