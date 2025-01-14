from dataclasses import dataclass, make_dataclass, asdict
from inspect import isclass
from typing import Sequence, Union, ClassVar
import ctypes as ct

from .internal import static_c_call, dds_c_t, DDS


class BasePolicy:
    pass


def _no_init(*args, **kwargs):
    raise NotImplementedError("This Qos object cannot be initialized like this.")

def _policy_singleton(scope, name):
    return make_dataclass(
        f"Policy.{scope}.{name}", [], 
        bases=(BasePolicy,), 
        namespace={'__scope__': scope, '__repr__': lambda s: f"Policy.{scope}.{name}"},
        frozen=True)()


class Policy:
    """The Policy class is fully static and should never need to be instantiated.

    See Also
    --------
    qoshowto: How to work with Qos and Policy, TODO.
    """
    __init__ = _no_init

    class Reliability:
        """The Reliability Qos Policy

        Examples
        --------
        >>> Policy.Reliability.BestEffort(max_blocking_time=duration(seconds=1))
        >>> Policy.Reliability.Reliable(max_blocking_time=duration(seconds=1))
        """
        __scope__ = "Reliability"
        __init__ = _no_init

        @dataclass(frozen=True)
        class BestEffort(BasePolicy):
            """Use BestEffort reliability

            Parameters
            ----------
            max_blocking_time : int
                The number of nanoseconds the writer will bock when its history is full.
                Use the :func:`duration<cdds.util.duration>` function to avoid time calculation headaches.
            """
            __scope__: ClassVar[str] = "Reliability"
            max_blocking_time: int

        @dataclass(frozen=True)
        class Reliable(BasePolicy):
            """Use Reliable reliability

            Parameters
            ----------
            max_blocking_time : int
                The number of nanoseconds the writer will bock when its history is full.
                Use the :func:`duration<cdds.util.duration>` function to avoid time calculation headaches.

            """
            __scope__: ClassVar[str] = "Reliability"
            max_blocking_time: int

    class Durability:
        """ The Durability Qos Policy

        Examples
        --------
        >>> Policy.Durability.Volatile
        >>> Policy.Durability.TransientLocal
        >>> Policy.Durability.Transient
        >>> Policy.Durability.Persistent
        """
        __init__ = _no_init
        __scope__ = "Durability"

        Volatile: 'Policy.Durability.Volatile' = _policy_singleton("Durability", "Volatile")
        TransientLocal: 'Policy.Durability.TransientLocal' = _policy_singleton("Durability", "TransientLocal")
        Transient: 'Policy.Durability.Transient' = _policy_singleton("Durability", "Transient")
        Persistent: 'Policy.Durability.Persistent' = _policy_singleton("Durability", "Persistent")

    class History:
        """ The History Qos Policy

        Examples
        --------
        >>> Policy.History.KeepAll
        >>> Policy.History.KeepLast(amount=10)

        Attributes
        ----------
        KeepAll: Tuple[PolicyType, Any]
                 The type of this entity is not publicly specified.
        """
        __init__ = _no_init
        __scope__ = "History"

        KeepAll: 'Policy.History.KeepAll' = _policy_singleton("History", "KeepAll")

        @dataclass(frozen=True)
        class KeepLast(BasePolicy):
            """
            Parameters
            ----------
            depth : int
                The depth of samples to keep in the history.
            """
            __scope__: ClassVar[str] = "History"
            depth: int

    @dataclass(frozen=True)
    class ResourceLimits(BasePolicy):
        """The ResourceLimits Qos Policy

        Examples
        --------
        >>> Policy.ResourceLimits(
        >>>     max_samples=10,
        >>>     max_instances=10,
        >>>     max_samples_per_instance=2
        >>> )

        Attributes
        ----------
        max_samples : int
            Max number of samples total.
        max_instances : int
            Max number of instances total.
        max_samples_per_instance : int
            Max number of samples per instance.
        """
        __scope__: ClassVar[str] = "ResourceLimits"
        max_samples: int = -1
        max_instances: int = -1
        max_samples_per_instance: int = -1

    class PresentationAccessScope:
        """The Presentation Access Scope Qos Policy

        Examples
        --------
        >>> Policy.PresentationAccessScope.Instance(coherent_access=True, ordered_access=False)
        >>> Policy.PresentationAccessScope.Topic(coherent_access=True, ordered_access=False)
        >>> Policy.PresentationAccessScope.Group(coherent_access=True, ordered_access=False)
        """
        __init__ = _no_init
        __scope__ = "PresentationAccessScope"

        @dataclass(frozen=True)
        class Instance(BasePolicy):
            """Use Instance Presentation Access Scope

            Attributes
            ----------
            coherent_access : bool
                Enable coherent access
            ordered_access : bool
                Enable ordered access
            """
            __scope__: ClassVar[str] = "PresentationAccessScope"
            coherent_access: bool
            ordered_access: bool

        @dataclass(frozen=True)
        class Topic(BasePolicy):
            """Use Topic Presentation Access Scope

            Attributes
            ----------
            coherent_access : bool
                Enable coherent access
            ordered_access : bool
                Enable ordered access
            """
            __scope__: ClassVar[str] = "PresentationAccessScope"
            coherent_access: bool
            ordered_access: bool

        @dataclass(frozen=True)
        class Group(BasePolicy):
            """Use Group Presentation Access Scope

            Attributes
            ----------
            coherent_access : bool
                Enable coherent access
            ordered_access : bool
                Enable ordered access
            """
            __scope__: ClassVar[str] = "PresentationAccessScope"
            coherent_access: bool
            ordered_access: bool

    @dataclass(frozen=True)
    class Lifespan(BasePolicy):
        """The Lifespan Qos Policy

        Examples
        --------
        >>> Policy.Lifespan(duration(seconds=2))

        Attributes
        ----------
        lifespan : int
            Expiration time relative to the source timestamp of a sample in nanoseconds.
        """
        __scope__: ClassVar[str] = "Lifespan"
        lifespan: int

    @dataclass(frozen=True)
    class Deadline(BasePolicy):
        """The Deadline Qos Policy

        Examples
        --------
        >>> Policy.Deadline(deadline=duration(seconds=2))

        Attributes
        ----------
        deadline : int
            Deadline of a sample in nanoseconds.
        """
        __scope__: ClassVar[str] = "Deadline"
        deadline: int

    @dataclass(frozen=True)
    class LatencyBudget(BasePolicy):
        """The Latency Budget Qos Policy

        Examples
        --------
        >>> Policy.LatencyBudget(duration(seconds=2))

        Parameters
        ----------
        budget : int
            Latency budget in nanoseconds.
        """
        __scope__: ClassVar[str] = "LatencyBudget"
        budget: int

    class Ownership:
        """The Ownership Qos Policy

        Examples
        --------
        >>> Policy.Ownership.Shared
        >>> Policy.Ownership.Exclusive

        Attributes
        ----------
        Shared:    Policy.Ownership.Shared
        Exclusive: Policy.Ownership.Exclusive
        """
        __init__ = _no_init
        __scope__ = "Ownership"

        Shared: 'Policy.Ownership.Shared' = _policy_singleton("Ownership", "Shared")
        Exclusive: 'Policy.Ownership.Exclusive' = _policy_singleton("Ownership", "Exclusive")

    @dataclass(frozen=True)
    class OwnershipStrength(BasePolicy):
        """The Ownership Strength Qos Policy

        Examples
        --------
        >>> Policy.OwnershipStrength(strength=2)

        Parameters
        ----------
        strength : int
            Ownership strength as integer.
        """
        __scope__: ClassVar[str] = "OwnershipStrength"
        strength: int

    class Liveliness:
        """The Liveliness Qos Policy

        Examples
        --------
        >>> Policy.Liveliness.Automatic(lease_duration=duration(seconds=10))
        >>> Policy.Liveliness.ManualByParticipant(lease_duration=duration(seconds=10))
        >>> Policy.Liveliness.ManualByTopic(lease_duration=duration(seconds=10))
        """
        __init__ = _no_init
        __scope__ = "Liveliness"

        @dataclass(frozen=True) 
        class Automatic(BasePolicy):
            """Use Automatic Liveliness

            Attributes
            ----------
            lease_duration: int
                The lease duration in nanoseconds. Use the helper function :func:`duration<cdds.util.duration>` to write
                the duration in a human readable format.
            """
            __scope__: ClassVar[str] = "Liveliness"
            lease_duration: int

        @dataclass(frozen=True) 
        class ManualByParticipant(BasePolicy):
            """Use ManualByParticipant Liveliness

            Attributes
            ----------
            lease_duration: int
                The lease duration in nanoseconds. Use the helper function :func:`duration<cdds.util.duration>` to write
                the duration in a human readable format.
            """
            __scope__: ClassVar[str] = "Liveliness"
            lease_duration: int

        @dataclass(frozen=True) 
        class ManualByTopic(BasePolicy):
            """Use ManualByTopic Liveliness

            Attributes
            ----------
            lease_duration: int
                The lease duration in nanoseconds. Use the helper function :func:`duration<cdds.util.duration>` to write
                the duration in a human readable format.
            """
            __scope__: ClassVar[str] = "Liveliness"
            lease_duration: int

    @dataclass(frozen=True)
    class TimeBasedFilter(BasePolicy):
        """The TimeBasedFilter Qos Policy

        Examples
        --------
        >>> Policy.TimeBasedFilter(filter_fn=duration(seconds=2))

        Attributes
        ----------
        filter_time: int
            Minimum time between samples in nanoseconds.  Use the helper function :func:`duration<cdds.util.duration>`
            to write the duration in a human readable format.
        """
        __scope__: ClassVar[str] = "TimeBasedFilter"
        filter_time: int

    @dataclass(frozen=True)
    class Partition(BasePolicy):
        """The Partition Qos Policy

        Examples
        --------
        >>> Policy.Partition(partitions=["partition_a", "partition_b", "partition_c"])
        >>> Policy.Partition(partitions=[f"partition_{i}" for i in range(100)])

        Attributes
        ----------
        partitions : Sequence[str]
        """
        __scope__: ClassVar[str] = "Partition"
        partitions: Sequence[str]

        def __post_init__(self):
            # Tuple-fy partitions to ensure immutability
            super().__setattr__('partitions', tuple(getattr(self, 'partitions')))
    
    @dataclass(frozen=True)
    class TransportPriority(BasePolicy):
        __scope__: ClassVar[str] = "TransportPriority"
        priority: int

    class DestinationOrder:
        __scope__: ClassVar[str] = "DestinationOrder"
        ByReceptionTimestamp: 'Policy.DestinationOrder.ByReceptionTimestamp' = \
            _policy_singleton("DestinationOrder", "ByReceptionTimestamp")
        BySourceTimestamp: 'Policy.DestinationOrder.BySourceTimestamp' = \
            _policy_singleton("DestinationOrder", "BySourceTimestamp")

    @dataclass(frozen=True)
    class WriterDataLifecycle(BasePolicy):
        __scope__: ClassVar[str] = "WriterDataLifecycle"
        autodispose: bool

    @dataclass(frozen=True)
    class ReaderDataLifecycle(BasePolicy):
        __scope__: ClassVar[str] = "ReaderDataLifecycle"
        autopurge_nowriter_samples_delay: int
        autopurge_disposed_samples_delay: int

    @dataclass(frozen=True)
    class DurabilityService(BasePolicy):
        __scope__: ClassVar[str] = "DurabilityService"
        cleanup_delay: int
        history: Union['Policy.History.KeepAll', 'Policy.History.KeepLast']
        max_samples: int
        max_instances: int
        max_samples_per_instance: int

    class IgnoreLocal:
        __init__ = _no_init
        __scope__ = "IgnoreLocal"

        Nothing: 'Policy.IgnoreLocal.Nothing' = _policy_singleton("IgnoreLocal", "Nothing")
        Participant: 'Policy.IgnoreLocal.Participant' = _policy_singleton("IgnoreLocal", "Participant")
        Process: 'Policy.IgnoreLocal.Process' = _policy_singleton("IgnoreLocal", "Process")

    @dataclass(frozen=True)
    class Userdata(BasePolicy):
        __scope__: ClassVar[str] = "Userdata"
        data: bytes

    @dataclass(frozen=True)
    class Topicdata(BasePolicy):
        __scope__: ClassVar[str] = "Topicdata"
        data: bytes

    @dataclass(frozen=True)
    class Groupdata(BasePolicy):
        __scope__: ClassVar[str] = "Groupdata"
        data: bytes


class Qos: 
    _policy_mapper = {
        "Policy.Reliability.BestEffort": Policy.Reliability.BestEffort,
        "Policy.Reliability.Reliable": Policy.Reliability.Reliable,
        "Policy.Durability.Volatile": Policy.Durability.Volatile,
        "Policy.Durability.TransientLocal": Policy.Durability.TransientLocal,
        "Policy.Durability.Transient": Policy.Durability.Transient,
        "Policy.Durability.Persistent": Policy.Durability.Persistent,
        "Policy.History.KeepAll": Policy.History.KeepAll,
        "Policy.History.KeepLast": Policy.History.KeepLast,
        "Policy.ResourceLimits": Policy.ResourceLimits,
        "Policy.PresentationAccessScope.Instance": Policy.PresentationAccessScope.Instance,
        "Policy.PresentationAccessScope.Topic": Policy.PresentationAccessScope.Topic,
        "Policy.PresentationAccessScope.Group": Policy.PresentationAccessScope.Group,
        "Policy.Lifespan": Policy.Lifespan,
        "Policy.Deadline": Policy.Deadline,
        "Policy.LatencyBudget": Policy.LatencyBudget,
        "Policy.Ownership.Shared": Policy.Ownership.Shared,
        "Policy.Ownership.Exclusive": Policy.Ownership.Exclusive,
        "Policy.OwnershipStrength": Policy.OwnershipStrength,
        "Policy.Liveliness.Automatic": Policy.Liveliness.Automatic,
        "Policy.Liveliness.ManualByParticipant": Policy.Liveliness.ManualByParticipant,
        "Policy.Liveliness.ManualByTopic": Policy.Liveliness.ManualByTopic,
        "Policy.TimeBasedFilter": Policy.TimeBasedFilter,
        "Policy.Partition": Policy.Partition,
        "Policy.TransportPriority": Policy.TransportPriority,
        "Policy.DestinationOrder.ByReceptionTimestamp": Policy.DestinationOrder.ByReceptionTimestamp,
        "Policy.DestinationOrder.BySourceTimestamp": Policy.DestinationOrder.BySourceTimestamp,
        "Policy.WriterDataLifecycle": Policy.WriterDataLifecycle,
        "Policy.ReaderDataLifecycle": Policy.ReaderDataLifecycle,
        "Policy.DurabilityService": Policy.DurabilityService,
        "Policy.IgnoreLocal.Nothing": Policy.IgnoreLocal.Nothing,
        "Policy.IgnoreLocal.Participant": Policy.IgnoreLocal.Participant,
        "Policy.IgnoreLocal.Process": Policy.IgnoreLocal.Process,
        "Policy.Userdata": Policy.Userdata,
        "Policy.Groupdata": Policy.Groupdata,
        "Policy.Topicdata": Policy.Topicdata
    }

    def __init__(self, *policies, base=None):
        policies = list(policies)
        for p in policies:
            if not isinstance(p, BasePolicy):
                raise TypeError(f"{repr(p)} is not a Policy.")

        if base is not None:
            if not isinstance(base, Qos):
                raise TypeError("base takes a Qos as argument.")
            for policy in base.policies:
                for p in policies:
                    if p.__scope__ == policy.__scope__:
                        break
                else:
                    policies.append(policy)

        self.__policies = tuple(sorted(policies, key=lambda x: x.__scope__))
        self._assert_consistency()

    def _assert_consistency(self):
        for i in range(len(self.__policies)):
            if not isinstance(self.__policies[i], BasePolicy):
                raise TypeError(str(self.__policies[i]), " is not a Policy.")
            
        for i in range(1, len(self.__policies)):
            if self.__policies[i-1].__scope__ == self.__policies[i].__scope__:
                raise ValueError("Multiple Qos policies of type {}.".format(self.__policies[i].__scope__))

    @property
    def policies(self):
        return self.__policies

    def __iter__(self):
        return iter(self.policies)

    def __getitem__(self, key):
        if not hasattr(key, "__scope__"):
            raise ValueError(f"{key} is not a valid policy to look up in the qos")
        scope = key.__scope__
        for p in self.__policies:
            if p.__scope__ > scope:
                break
            if p.__scope__ == scope:
                return p
        return None

    def __contains__(self, key):
        if not hasattr(key, "__scope__"):
            raise ValueError(f"{key} is not a valid policy to look up in the qos")
        if isclass(key):
            scope = key.__scope__
            for p in self.__policies:
                if p.__scope__ > scope:
                    break
                if p.__scope__ == scope:
                    return True
        else:
            scope = key.__scope__
            for p in self.__policies:
                if p.__scope__ > scope:
                    break
                if p == key:
                    return True
        return False


    def __len__(self):
        return len(self.__policies)

    def __eq__(self, other):
        if not isinstance(other, Qos):
            return False

        if len(self.policies) != len(other.policies):
            return False

        for p, q in zip(self.policies, other.policies):
            if p != q:
                return False
        return True

    def __repr__(self):
        return "Qos({})".format(", ".join(repr(p) for p in sorted(self.policies)))

    __str__ = __repr__

    def asdict(self):
        ret = {}
        for p in self.policies:
            path = p.__class__.__qualname__.split(".")
            data = asdict(p)
            if len(path) == 2:
                ret[path[1]] = data
            else:  # if len(path) == 3:
                ret[path[1]] = {"kind": path[2]}
                if data:
                    ret[path[1]].update(data)
        return ret

    @classmethod
    def fromdict(cls, data: dict):
        policies = []
        for k, v in data.items():
            # Special case
            if k == "DurabilityService":
                if not v["history"]:
                    v["history"] = Policy.History.KeepAll
                else:
                    v["history"] = Policy.History.KeepLast(v["history"]["depth"])

            name = f"Policy.{k}"
            if name in cls._policy_mapper:
                if v:
                    policies.append(cls._policy_mapper[name](**v))
                else:
                    policies.append(cls._policy_mapper[name])
                continue
            if "kind" in v:
                name += f".{v['kind']}"
                del v["kind"]
                if name in cls._policy_mapper:
                    if v:
                        policies.append(cls._policy_mapper[name](**v))
                    else:
                        policies.append(cls._policy_mapper[name])
                    continue
            raise ValueError("Not a valid Qos dictionary.")

        return cls(*policies)


class _CQos(DDS):
    _all_scopes = (
        "Reliability", "Durability", "History", "ResourceLimits", "PresentationAccessScope",
        "Lifespan", "Deadline", "LatencyBudget", "Ownership", "OwnershipStrength",
        "Liveliness", "TimeBasedFilter", "Partition", "TransportPriority",
        "DestinationOrder", "WriterDataLifecycle", "ReaderDataLifecycle",
        "DurabilityService", "IgnoreLocal", "Userdata", "Groupdata", "Topicdata",
    )

    @classmethod
    def cqos_create(cls):
        return cls._create_qos()

    @classmethod
    def qos_to_cqos(cls, qos: Qos):
        cqos = cls._create_qos()

        for policy in qos:
            getattr(cls, "_set_p_" + policy.__scope__.lower())(cqos, policy)

        return cqos

    @classmethod
    def cqos_to_qos(cls, cqos):
        policies = []
        for scope in cls._all_scopes:
            p = getattr(cls, "_get_p_" + scope.lower())(cqos)
            if p is not None:
                policies.append(p)

        return Qos(*policies)

    @classmethod
    def cqos_destroy(cls, cqos):
        cls.delete_cqos(cqos)

    @static_c_call("dds_create_qos")
    def _create_qos(self) -> dds_c_t.qos_p:
        pass

    @static_c_call("dds_delete_qos")
    def delete_cqos(self, qos: dds_c_t.qos_p) -> None:
        pass

    # Reliability

    @classmethod
    def _set_p_reliability(cls, qos, policy):
        if type(policy) is Policy.Reliability.BestEffort:
            return cls._set_reliability(qos, 0, policy.max_blocking_time)
        return cls._set_reliability(qos, 1, policy.max_blocking_time)

    @static_c_call("dds_qset_reliability")
    def _set_reliability(self, qos: dds_c_t.qos_p, reliability_kind: dds_c_t.reliability,
                         blocking_time: dds_c_t.duration) -> None:
        pass

    # Durability

    @classmethod
    def _set_p_durability(cls, qos, policy):
        if policy == Policy.Durability.Volatile:
            return cls._set_durability(qos, 0)
        elif policy == Policy.Durability.TransientLocal:
            return cls._set_durability(qos, 1)
        elif policy == Policy.Durability.Transient:
            return cls._set_durability(qos, 2)
        return cls._set_durability(qos, 3)

    @static_c_call("dds_qset_durability")
    def _set_durability(self, qos: dds_c_t.qos_p, durability_kind: dds_c_t.durability) -> None:
        pass

    # History

    @classmethod
    def _set_p_history(cls, qos, policy):
        if policy == Policy.History.KeepAll:
            return cls._set_history(qos, 1, 0)
        return cls._set_history(qos, 0, policy.depth)

    @static_c_call("dds_qset_history")
    def _set_history(self, qos: dds_c_t.qos_p, history_kind: dds_c_t.history, depth: ct.c_int32) -> None:
        pass

    # Resource Limits

    @classmethod
    def _set_p_resourcelimits(cls, qos, policy):
        return cls._set_resource_limits(qos, policy.max_samples, policy.max_instances, policy.max_samples_per_instance)

    @static_c_call("dds_qset_resource_limits")
    def _set_resource_limits(self, qos: dds_c_t.qos_p, max_samples: ct.c_int32, max_instances: ct.c_int32,
                             max_samples_per_instance: ct.c_int32) -> None:
        pass

    # Presentation access scpoe

    @classmethod
    def _set_p_presentationaccessscope(cls, qos, policy):
        if type(policy) is Policy.PresentationAccessScope.Instance:
            return cls._set_presentation_access_scope(qos, 0, policy.coherent_access, policy.ordered_access)
        elif type(policy) is Policy.PresentationAccessScope.Topic:
            return cls._set_presentation_access_scope(qos, 1, policy.coherent_access, policy.ordered_access)
        return cls._set_presentation_access_scope(qos, 2, policy.coherent_access, policy.ordered_access)


    @static_c_call("dds_qset_presentation")
    def _set_presentation_access_scope(self, qos: dds_c_t.qos_p, access_scope: dds_c_t.presentation_access_scope,
                                       coherent_access: ct.c_bool, ordered_access: ct.c_bool) -> None:
        pass

    # Lifespan

    @classmethod
    def _set_p_lifespan(cls, qos, policy):
        return cls._set_lifespan(qos, policy.lifespan)

    @static_c_call("dds_qset_lifespan")
    def _set_lifespan(self, qos: dds_c_t.qos_p, lifespan: dds_c_t.duration) -> None:
        pass

    # Deadline

    @classmethod
    def _set_p_deadline(cls, qos, policy):
        return cls._set_deadline(qos, policy.deadline)

    @static_c_call("dds_qset_deadline")
    def _set_deadline(self, qos: dds_c_t.qos_p, deadline: dds_c_t.duration) -> None:
        pass

    # Latency budget

    @classmethod
    def _set_p_latencybudget(cls, qos, policy):
        return cls._set_latency_budget(qos, policy.budget)

    @static_c_call("dds_qset_latency_budget")
    def _set_latency_budget(self, qos: dds_c_t.qos_p, latency_budget: dds_c_t.duration) -> None:
        pass

    # Ownership

    @classmethod
    def _set_p_ownership(cls, qos, policy):
        if policy == Policy.Ownership.Shared:
            return cls._set_ownership(qos, 0)
        return cls._set_ownership(qos, 1)

    @static_c_call("dds_qset_ownership")
    def _set_ownership(self, qos: dds_c_t.qos_p, ownership_kind: dds_c_t.ownership) -> None:
        pass

    # Ownership Strength

    @classmethod
    def _set_p_ownershipstrength(cls, qos, policy):
        return cls._set_ownership_strength(qos, policy.strength)

    @static_c_call("dds_qset_ownership_strength")
    def _set_ownership_strength(self, qos: dds_c_t.qos_p, ownership_strength: ct.c_int32) -> None:
        pass

    # Liveliness

    @classmethod
    def _set_p_liveliness(cls, qos, policy):
        if type(policy) is Policy.Liveliness.Automatic:
            return cls._set_liveliness(qos, 0, policy.lease_duration)
        elif type(policy) is Policy.Liveliness.ManualByParticipant:
            return cls._set_liveliness(qos, 1, policy.lease_duration)
        return cls._set_liveliness(qos, 2, policy.lease_duration)

    @static_c_call("dds_qset_liveliness")
    def _set_liveliness(self, qos: dds_c_t.qos_p, liveliness_kind: dds_c_t.liveliness,
                        lease_duration: dds_c_t.duration) -> None:
        pass

    # Time based filter

    @classmethod
    def _set_p_timebasedfilter(cls, qos, policy):
        return cls._set_time_based_filter(qos, policy.filter_time)

    @static_c_call("dds_qset_time_based_filter")
    def _set_time_based_filter(self, qos: dds_c_t.qos_p, minimum_separation: dds_c_t.duration) -> None:
        pass

    # Partition

    @classmethod
    def _set_p_partition(cls, qos, policy):
        ps = [p.encode() for p in policy.partitions]
        p_pt = (ct.c_char_p * len(ps))()
        for i, p in enumerate(ps):
            p_pt[i] = p
        cls._set_partition(qos, len(ps), p_pt)

    @static_c_call("dds_qset_partition")
    def _set_partition(self, qos: dds_c_t.qos_p, n: ct.c_uint32, ps: ct.POINTER(ct.c_char_p)) -> None:
        pass

    # Transport priority

    @classmethod
    def _set_p_transportpriority(cls, qos, policy):
        return cls._set_transport_priority(qos, policy.priority)

    @static_c_call("dds_qset_transport_priority")
    def _set_transport_priority(self, qos: dds_c_t.qos_p, value: ct.c_int32) -> None:
        pass

    # Destination order

    @classmethod
    def _set_p_destinationorder(cls, qos, policy):
        if policy == Policy.DestinationOrder.ByReceptionTimestamp:
            return cls._set_destination_order(qos, 0)
        return cls._set_destination_order(qos, 1)

    @static_c_call("dds_qset_destination_order")
    def _set_destination_order(self, qos: dds_c_t.qos_p, destination_order_kind: dds_c_t.destination_order) -> None:
        pass

    # Writer Data Lifecycle

    @classmethod
    def _set_p_writerdatalifecycle(cls, qos, policy):
        return cls._set_writer_data_lifecycle(qos, policy.autodispose)

    @static_c_call("dds_qset_writer_data_lifecycle")
    def _set_writer_data_lifecycle(self, qos: dds_c_t.qos_p, autodispose: ct.c_bool) -> None:
        pass

    # Reader Data Lifecycle

    @classmethod
    def _set_p_readerdatalifecycle(cls, qos, policy):
        return cls._set_reader_data_lifecycle(
            qos, 
            policy.autopurge_nowriter_samples_delay,
            policy.autopurge_disposed_samples_delay
        )

    @static_c_call("dds_qset_reader_data_lifecycle")
    def _set_reader_data_lifecycle(self, qos: dds_c_t.qos_p, autopurge_nowriter_samples_delay: dds_c_t.duration,
                                   autopurge_disposed_samples_delay: dds_c_t.duration) -> None:
        pass

    # Durability Service

    @classmethod
    def _set_p_durabilityservice(cls, qos, policy):
        if policy.history == Policy.History.KeepAll:
            history_kind = 1
            history_depth = 0
        else:
            history_kind = 0
            history_depth = policy.history.depth

        return cls._set_durability_service(
            qos,
            policy.cleanup_delay,
            history_kind,
            history_depth,
            policy.max_samples,
            policy.max_instances,
            policy.max_samples_per_instance
        )

    @static_c_call("dds_qset_durability_service")
    def _set_durability_service(self, qos: dds_c_t.qos_p, service_cleanup_delay: dds_c_t.duration,
                                history_kind: dds_c_t.history, history_depth: ct.c_int32, max_samples: ct.c_int32,
                                max_instances: ct.c_int32, max_samples_per_instance: ct.c_int32) -> None:
        pass

    # Ignore local

    @classmethod
    def _set_p_ignorelocal(cls, qos, policy):
        if policy == Policy.IgnoreLocal.Nothing:
            return cls._set_ignore_local(qos, 0)
        elif policy == Policy.IgnoreLocal.Participant:
            return cls._set_ignore_local(qos, 1)
        return cls._set_ignore_local(qos, 2)

    @static_c_call("dds_qset_ignorelocal")
    def _set_ignore_local(self, qos: dds_c_t.qos_p, ingorelocal_kind: dds_c_t.ingnorelocal) -> None:
        pass

    # Userdata

    @classmethod
    def _set_p_userdata(cls, qos, policy):
        cls._set_userdata(qos, policy.data, len(policy.data))
    
    @static_c_call("dds_qset_userdata")
    def _set_userdata(self, qos: dds_c_t.qos_p, value: ct.c_void_p, size: ct.c_size_t) -> None:
        pass

    # Topic

    @classmethod
    def _set_p_topicdata(cls, qos, policy):
        cls._set_topicdata(qos, policy.data, len(policy.data))

    @static_c_call("dds_qset_topicdata")
    def _set_topicdata(self, qos: dds_c_t.qos_p, value: ct.c_void_p, size: ct.c_size_t) -> None:
        pass

    # Group

    @classmethod
    def _set_p_groupdata(cls, qos, policy):
        cls._set_groupdata(qos, policy.data, len(policy.data))

    @static_c_call("dds_qset_groupdata")
    def _set_groupdata(self, qos: dds_c_t.qos_p, value: ct.c_void_p, size: ct.c_size_t) -> None:
        pass

    #### END OF SETTERS, START OF GETTERS ####
    _gc_data_size = ct.c_size_t()
    _gc_data_value = ct.c_void_p()
    _gc_durability = dds_c_t.durability()
    _gc_history = dds_c_t.history()
    _gc_history_depth = ct.c_int32()
    _gc_max_samples = ct.c_int32()
    _gc_max_instances = ct.c_int32()
    _gc_max_samples_per_instance = ct.c_int32()
    _gc_access_scope = dds_c_t.presentation_access_scope()
    _gc_coherent_access = ct.c_bool()
    _gc_ordered_access = ct.c_bool()
    _gc_lifespan = dds_c_t.duration()
    _gc_deadline = dds_c_t.duration()
    _gc_latency_budget = dds_c_t.duration()
    _gc_ownership = dds_c_t.ownership()
    _gc_ownership_strength = ct.c_int32()
    _gc_liveliness = dds_c_t.liveliness()
    _gc_lease_duration = dds_c_t.duration()
    _gc_time_based_filter = dds_c_t.duration()
    _gc_partition_num = ct.c_uint32()
    _gc_partition_names = (ct.POINTER(ct.c_char_p))()
    _gc_reliability = dds_c_t.reliability()
    _gc_max_blocking_time = dds_c_t.duration()
    _gc_transport_priority = ct.c_int32()
    _gc_destination_order = dds_c_t.destination_order()
    _gc_writer_autodispose = ct.c_bool()
    _gc_autopurge_nowriter_samples_delay = dds_c_t.duration()
    _gc_autopurge_disposed_samples_delay = dds_c_t.duration()
    _gc_durservice_service_cleanup_delay = dds_c_t.duration()
    _gc_durservice_history_kind = dds_c_t.history()
    _gc_durservice_history_depth = ct.c_int32()
    _gc_durservice_max_samples = ct.c_int32()
    _gc_durservice_max_instances = ct.c_int32()
    _gc_durservice_max_samples_per_instance = ct.c_int32()
    _gc_ignorelocal = dds_c_t.ingnorelocal()
    _gc_propnames_num = ct.c_uint32()
    _gc_propnames_names = (ct.POINTER(ct.c_char_p))()
    _gc_prop_get_value = ct.c_char_p()
    _gc_bpropnames_num = ct.c_uint32()
    _gc_bpropnames_names = (ct.POINTER(ct.c_char_p))()
    _gc_bprop_get_value = ct.c_char_p()

    # Reliability

    @classmethod
    def _get_p_reliability(cls, qos):
        if not cls._get_reliability(qos, ct.byref(cls._gc_reliability), ct.byref(cls._gc_max_blocking_time)):
            return None

        if cls._gc_reliability.value == 0:
            return Policy.Reliability.BestEffort(max_blocking_time=cls._gc_max_blocking_time.value)
        return Policy.Reliability.Reliable(max_blocking_time=cls._gc_max_blocking_time.value)

    @static_c_call("dds_qget_reliability")
    def _get_reliability(self, qos: dds_c_t.qos_p, reliability_kind: ct.POINTER(dds_c_t.reliability),
                         blocking_time: ct.POINTER(dds_c_t.duration)) -> bool:
        pass

    # Durability

    @classmethod
    def _get_p_durability(cls, qos):
        if not cls._get_durability(qos, ct.byref(cls._gc_durability)):
            return None

        if cls._gc_durability.value == 0:
            return Policy.Durability.Volatile
        elif cls._gc_durability.value == 1:
            return Policy.Durability.TransientLocal
        elif cls._gc_durability.value == 2:
            return Policy.Durability.Transient
        return Policy.Durability.Persistent

    @static_c_call("dds_qget_durability")
    def _get_durability(self, qos: dds_c_t.qos_p, durability_kind: ct.POINTER(dds_c_t.durability)) -> bool:
        pass

    # History

    @classmethod
    def _get_p_history(cls, qos):
        if not cls._get_history(qos, ct.byref(cls._gc_history), ct.byref(cls._gc_history_depth)):
            return None

        if cls._gc_history.value == 1:
            return Policy.History.KeepAll
        return Policy.History.KeepLast(depth=cls._gc_history_depth.value)

    @static_c_call("dds_qget_history")
    def _get_history(self, qos: dds_c_t.qos_p, history_kind: ct.POINTER(dds_c_t.history),
                     depth: ct.POINTER(ct.c_int32)) -> bool:
        pass

    # Resource limits

    @classmethod
    def _get_p_resourcelimits(cls, qos):
        if not cls._get_resource_limits(
                qos, ct.byref(cls._gc_max_samples),
                ct.byref(cls._gc_max_instances),
                ct.byref(cls._gc_max_samples_per_instance)):
            return None

        return Policy.ResourceLimits(
            max_samples=cls._gc_max_samples.value,
            max_instances=cls._gc_max_instances.value,
            max_samples_per_instance=cls._gc_max_samples_per_instance.value
        )

    @static_c_call("dds_qget_resource_limits")
    def _get_resource_limits(self, qos: dds_c_t.qos_p, max_samples: ct.POINTER(ct.c_int32),
                             max_instances: ct.POINTER(ct.c_int32),
                             max_samples_per_instance: ct.POINTER(ct.c_int32)) -> bool:
        pass

    # Presentation access scope

    @classmethod
    def _get_p_presentationaccessscope(cls, qos):
        if not cls._get_presentation(
                qos, ct.byref(cls._gc_access_scope),
                ct.byref(cls._gc_coherent_access),
                ct.byref(cls._gc_ordered_access)):
            return None

        if cls._gc_access_scope.value == 0:
            return Policy.PresentationAccessScope.Instance(
                coherent_access=cls._gc_coherent_access.value,
                ordered_access=cls._gc_ordered_access.value
            )
        elif cls._gc_access_scope.value == 1:
            return Policy.PresentationAccessScope.Topic(
                coherent_access=cls._gc_coherent_access.value,
                ordered_access=cls._gc_ordered_access.value
            )
        return Policy.PresentationAccessScope.Group(
            coherent_access=cls._gc_coherent_access.value,
            ordered_access=cls._gc_ordered_access.value
        )

    @static_c_call("dds_qget_presentation")
    def _get_presentation(self, qos: dds_c_t.qos_p, access_scope: ct.POINTER(dds_c_t.presentation_access_scope),
                          coherent_access: ct.POINTER(ct.c_bool), ordered_access: ct.POINTER(ct.c_bool)) -> bool:
        pass

    # Lifespan

    @classmethod
    def _get_p_lifespan(cls, qos):
        if not cls._get_lifespan(qos, ct.byref(cls._gc_lifespan)):
            return None

        return Policy.Lifespan(lifespan=cls._gc_lifespan.value)

    @static_c_call("dds_qget_lifespan")
    def _get_lifespan(self, qos: dds_c_t.qos_p, lifespan: ct.POINTER(dds_c_t.duration)) -> bool:
        pass

    # Deadline

    @classmethod
    def _get_p_deadline(cls, qos):
        if not cls._get_deadline(qos, ct.byref(cls._gc_deadline)):
            return None

        return Policy.Deadline(deadline=cls._gc_deadline.value)

    @static_c_call("dds_qget_deadline")
    def _get_deadline(self, qos: dds_c_t.qos_p, deadline: ct.POINTER(dds_c_t.duration)) -> bool:
        pass

    # Latency Budget

    @classmethod
    def _get_p_latencybudget(cls, qos):
        if not cls._get_latency_budget(qos, ct.byref(cls._gc_latency_budget)):
            return None

        return Policy.LatencyBudget(budget=cls._gc_latency_budget.value)

    @static_c_call("dds_qget_latency_budget")
    def _get_latency_budget(self, qos: dds_c_t.qos_p, latency_budget: ct.POINTER(dds_c_t.duration)) -> bool:
        pass

    # Ownership

    @classmethod
    def _get_p_ownership(cls, qos):
        if not cls._get_ownership(qos, ct.byref(cls._gc_ownership)):
            return None

        if cls._gc_ownership.value == 0:
            return Policy.Ownership.Shared
        return Policy.Ownership.Exclusive

    @static_c_call("dds_qget_ownership")
    def _get_ownership(self, qos: dds_c_t.qos_p, ownership_kind: ct.POINTER(dds_c_t.ownership)) -> bool:
        pass

    # Ownership strength

    @classmethod
    def _get_p_ownershipstrength(cls, qos):
        if not cls._get_ownership_strength(qos, ct.byref(cls._gc_ownership_strength)):
            return None

        return Policy.OwnershipStrength(strength=cls._gc_ownership_strength.value)

    @static_c_call("dds_qget_ownership_strength")
    def _get_ownership_strength(self, qos: dds_c_t.qos_p, strength: ct.POINTER(ct.c_int32)) -> bool:
        pass

    # Liveliness

    @classmethod
    def _get_p_liveliness(cls, qos):
        if not cls._get_liveliness(qos, ct.byref(cls._gc_liveliness), ct.byref(cls._gc_lease_duration)):
            return None

        if cls._gc_liveliness.value == 0:
            return Policy.Liveliness.Automatic(lease_duration=cls._gc_lease_duration.value)
        if cls._gc_liveliness.value == 1:
            return Policy.Liveliness.ManualByParticipant(lease_duration=cls._gc_lease_duration.value)
        return Policy.Liveliness.ManualByTopic(lease_duration=cls._gc_lease_duration.value)

    @static_c_call("dds_qget_liveliness")
    def _get_liveliness(self, qos: dds_c_t.qos_p, liveliness_kind: ct.POINTER(dds_c_t.liveliness),
                        lease_duration: ct.POINTER(dds_c_t.duration)) -> bool:
        pass

    # Time based filter
    @classmethod
    def _get_p_timebasedfilter(cls, qos):
        if not cls._get_time_based_filter(qos, ct.byref(cls._gc_time_based_filter)):
            return None

        return Policy.TimeBasedFilter(filter_time=cls._gc_time_based_filter.value)

    @static_c_call("dds_qget_time_based_filter")
    def _get_time_based_filter(self, qos: dds_c_t.qos_p, minimum_separation: ct.POINTER(dds_c_t.duration)) -> bool:
        pass

    # Partition

    @classmethod
    def _get_p_partition(cls, qos):
        if not cls._get_partition(qos, ct.byref(cls._gc_partition_num), ct.byref(cls._gc_partition_names)):
            return None

        if cls._gc_partition_num.value == 0:
            return None

        names = [None] * cls._gc_partition_num.value
        for i in range(cls._gc_partition_num.value):
            names[i] = bytes(cls._gc_partition_names[i]).decode()

        return Policy.Partition(partitions=names)

    @static_c_call("dds_qget_partition")
    def _get_partition(self, qos: dds_c_t.qos_p, n: ct.POINTER(ct.c_uint32), ps: ct.POINTER(ct.POINTER(ct.c_char_p))) -> bool:
        pass

    # Transport priority

    @classmethod
    def _get_p_transportpriority(cls, qos):
        if not cls._get_transport_priority(qos, ct.byref(cls._gc_transport_priority)):
            return None

        return Policy.TransportPriority(priority=cls._gc_transport_priority.value)

    @static_c_call("dds_qget_transport_priority")
    def _get_transport_priority(self, qos: dds_c_t.qos_p, value: ct.POINTER(ct.c_int32)) -> bool:
        pass

    # Destination order

    @classmethod
    def _get_p_destinationorder(cls, qos):
        if not cls._get_destination_order(qos, ct.byref(cls._gc_destination_order)):
            return None

        if cls._gc_destination_order.value == 0:
            return Policy.DestinationOrder.ByReceptionTimestamp
        return Policy.DestinationOrder.BySourceTimestamp

    @static_c_call("dds_qget_destination_order")
    def _get_destination_order(self, qos: dds_c_t.qos_p,
                               destination_order_kind: ct.POINTER(dds_c_t.destination_order)) -> bool:
        pass

    # Writer data lifecycle

    @classmethod
    def _get_p_writerdatalifecycle(cls, qos):
        if not cls._get_writer_data_lifecycle(qos, ct.byref(cls._gc_writer_autodispose)):
            return None

        return Policy.WriterDataLifecycle(autodispose=cls._gc_writer_autodispose.value)

    @static_c_call("dds_qget_writer_data_lifecycle")
    def _get_writer_data_lifecycle(self, qos: dds_c_t.qos_p, autodispose: ct.POINTER(ct.c_bool)) -> bool:
        pass

    # Reader data lifecycle

    @classmethod
    def _get_p_readerdatalifecycle(cls, qos):
        if not cls._get_reader_data_lifecycle(qos, ct.byref(cls._gc_autopurge_nowriter_samples_delay),
                                               ct.byref(cls._gc_autopurge_disposed_samples_delay)):
            return None

        return Policy.ReaderDataLifecycle(
            autopurge_nowriter_samples_delay=cls._gc_autopurge_nowriter_samples_delay.value,
            autopurge_disposed_samples_delay=cls._gc_autopurge_disposed_samples_delay.value
        )

    @static_c_call("dds_qget_reader_data_lifecycle")
    def _get_reader_data_lifecycle(self, qos: dds_c_t.qos_p,
                                   autopurge_nowriter_samples_delay: ct.POINTER(dds_c_t.duration),
                                   autopurge_disposed_samples_delay: ct.POINTER(dds_c_t.duration)) -> bool:
        pass

    # Durability service

    @classmethod
    def _get_p_durabilityservice(cls, qos):
        if not cls._get_durability_service(
                qos,
                ct.byref(cls._gc_durservice_service_cleanup_delay),
                ct.byref(cls._gc_durservice_history_kind),
                ct.byref(cls._gc_durservice_history_depth),
                ct.byref(cls._gc_durservice_max_samples),
                ct.byref(cls._gc_durservice_max_instances),
                ct.byref(cls._gc_durservice_max_samples_per_instance)):
            return None

        if cls._gc_durservice_history_kind.value == 0:
            history = Policy.History.KeepLast(depth=cls._gc_durservice_history_depth.value)
        else:
            history = Policy.History.KeepAll

        return Policy.DurabilityService(
            cleanup_delay=cls._gc_durservice_service_cleanup_delay.value,
            history=history,
            max_samples=cls._gc_durservice_max_samples.value,
            max_instances=cls._gc_durservice_max_instances.value,
            max_samples_per_instance=cls._gc_durservice_max_samples_per_instance.value
        )

    @static_c_call("dds_qget_durability_service")
    def _get_durability_service(self, qos: dds_c_t.qos_p, service_cleanup_delay: ct.POINTER(dds_c_t.duration),
                                history_kind: ct.POINTER(dds_c_t.history), history_depth: ct.POINTER(ct.c_int32),
                                max_samples: ct.POINTER(ct.c_int32), max_instances: ct.POINTER(ct.c_int32),
                                max_samples_per_instance: ct.POINTER(ct.c_int32)) -> bool:
        pass

    # Ignore local
    
    @classmethod
    def _get_p_ignorelocal(cls, qos):
        if not cls._get_ignorelocal(qos, ct.byref(cls._gc_ignorelocal)):
            return None

        if cls._gc_ignorelocal.value == 0:
            return Policy.IgnoreLocal.Nothing
        if cls._gc_ignorelocal.value == 1:
            return Policy.IgnoreLocal.Participant
        return Policy.IgnoreLocal.Process

    @static_c_call("dds_qget_ignorelocal")
    def _get_ignorelocal(self, qos: dds_c_t.qos_p, ingorelocal_kind: ct.POINTER(dds_c_t.ingnorelocal)) -> bool:
        pass

    # Userdata

    @classmethod
    def _get_p_userdata(cls, qos):
        if not cls._get_userdata(qos, ct.byref(cls._gc_data_value), ct.byref(cls._gc_data_size)):
            return None
        
        if cls._gc_data_size == 0 or not bool(cls._gc_data_value):
            return None

        byte_type = ct.c_byte * cls._gc_data_size.value
        mybytes = bytes(ct.cast(cls._gc_data_value, ct.POINTER(byte_type))[0])

        return Policy.Userdata(data=mybytes)
    
    @static_c_call("dds_qget_userdata")
    def _get_userdata(self, qos: dds_c_t.qos_p, value: ct.POINTER(ct.c_void_p), size: ct.POINTER(ct.c_size_t)) -> bool:
        pass

    # Topicdata

    @classmethod
    def _get_p_topicdata(cls, qos):
        if not cls._get_topicdata(qos, ct.byref(cls._gc_data_value), ct.byref(cls._gc_data_size)):
            return None
        
        if cls._gc_data_size == 0 or not bool(cls._gc_data_value):
            return None

        byte_type = ct.c_byte * cls._gc_data_size.value
        mybytes = bytes(ct.cast(cls._gc_data_value, ct.POINTER(byte_type))[0])

        return Policy.Topicdata(data=mybytes)

    @static_c_call("dds_qget_topicdata")
    def _get_topicdata(self, qos: dds_c_t.qos_p, value: ct.POINTER(ct.c_void_p), size: ct.POINTER(ct.c_size_t)) -> bool:
        pass

    # Groupdata

    @classmethod
    def _get_p_groupdata(cls, qos):
        if not cls._get_groupdata(qos, ct.byref(cls._gc_data_value), ct.byref(cls._gc_data_size)):
            return None
        
        if cls._gc_data_size == 0 or not bool(cls._gc_data_value):
            return None

        byte_type = ct.c_byte * cls._gc_data_size.value
        mybytes = bytes(ct.cast(cls._gc_data_value, ct.POINTER(byte_type))[0])

        return Policy.Groupdata(data=mybytes)

    @static_c_call("dds_qget_groupdata")
    def _get_groupdata(self, qos: dds_c_t.qos_p, value: ct.POINTER(ct.c_void_p), size: ct.POINTER(ct.c_size_t)) -> bool:
        pass
