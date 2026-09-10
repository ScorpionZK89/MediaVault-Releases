"""Server diagnostics; missing measurements remain unknown."""

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.entity import EntityCategory

from .entity import MediaVaultEntity

METRICS = (
    ("cpu", "CPU", "runtime", "cpuPercent", "%"),
    ("memory", "Memory", "runtime", "workingSetBytes", "B"),
    ("storage", "Storage used", "runtime", "storagePercent", "%"),
    ("streams", "Active streams", "streams", "activeStreams", None),
    ("transcodes", "Transcodes", "streams", "transcode", None),
    ("direct_play", "Direct play", "streams", "directPlay", None),
    ("direct_stream", "Direct stream", "streams", "directStream", None),
    ("tasks", "Active tasks", "activity", "activeCount", None),
    ("queued", "Queued tasks", "activity", "queuedCount", None),
    ("failed", "Recent failed tasks", "activity", "failedCount", None),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    if coordinator.data["permissions"].get("server"):
        async_add_entities(
            [MediaVaultMetric(coordinator, metric) for metric in METRICS]
        )
    added = set()

    def discover():
        entities = []
        for library in coordinator.data.get("libraries") or []:
            if library["id"] not in added:
                added.add(library["id"])
                entities.append(MediaVaultLibrary(coordinator, library))
        async_add_entities(entities)

    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))


class MediaVaultLibrary(MediaVaultEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:movie-open"

    def __init__(self, coordinator, library):
        self._id = library["id"]
        super().__init__(
            coordinator, f"library:{self._id}", f"{library['name']} titles"
        )

    @property
    def native_value(self):
        return next(
            (
                item["mediaCount"]
                for item in self.coordinator.data.get("libraries") or []
                if item["id"] == self._id
            ),
            None,
        )

    @property
    def available(self):
        return super().available and self.native_value is not None


class MediaVaultMetric(MediaVaultEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, metric):
        key, name, self._section, self._field, unit = metric
        super().__init__(coordinator, key, name)
        self._attr_native_unit_of_measurement = unit

    @property
    def available(self):
        return (
            super().available
            and self.coordinator.data["permissions"].get("server", False)
            and self.coordinator.data.get(self._section) is not None
        )

    @property
    def native_value(self):
        return (self.coordinator.data.get(self._section) or {}).get(self._field)

    @property
    def extra_state_attributes(self):
        if self._field == "activeCount":
            # Bounded, non-secret task IDs allow explicit pause/resume/cancel automation.
            return {
                "tasks": [
                    {
                        key: item.get(key)
                        for key in (
                            "id",
                            "title",
                            "status",
                            "progressPercent",
                            "canPause",
                            "canResume",
                            "canCancel",
                        )
                    }
                    for item in (self.coordinator.data.get("activity") or {}).get(
                        "active", []
                    )[:50]
                ],
                "entry_id": self.coordinator.config_entry.entry_id,
            }
        return None
