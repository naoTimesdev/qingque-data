from __future__ import annotations

import functools
from enum import Enum
from typing import Any, Literal, TypedDict, cast

import msgspec
import orjson
from msgspec import Struct, field
from sr_common import (
    ROOT_DIR,
    Hashable,
    get_hash_content,
    load_all_languages,
    read_config,
    remap_icon_or_image,
)


class _MessageSectionConfigOptional(TypedDict, total=False):
    IsPerformMessage: bool
    MainMissionLink: int


class _MessageSectionConfig(_MessageSectionConfigOptional):
    ID: int
    StartMessageItemIDList: list[int]


class _MessageItemConfig(TypedDict):
    ID: int
    Sender: Literal["Player", "PlayerAuto", "NPC", "System"]
    ItemType: Literal["Text", "Image", "Sticker", "Raid"]
    MainText: Hashable
    OptionText: Hashable
    NextItemIDList: list[int]
    SectionID: int
    """Message section/group"""
    ContactsID: int
    ItemContentID: int


class _MessageGroupConfig(TypedDict):
    ID: int
    MessageContactsID: int
    MessageSectionIDList: list[int]


class _MessageContactsConfigOptional(TypedDict, total=False):
    ContactsType: int
    ContactsCamp: int


class _MessageContactsConfig(_MessageContactsConfigOptional):
    ID: int
    Name: Hashable
    SignatureText: Hashable
    IconPath: str


class _MessageItemImageConfig(TypedDict):
    ID: int
    ImagePath: str


class _MessageItemRaidEntranceConfig(TypedDict):
    ID: int
    RaidID: int
    ImagePath: str


class _SimpleRaidConfig(TypedDict):
    RaidID: int
    RaidName: Hashable
    RaidDesc: Hashable


class _SimpleEmojiConfig(TypedDict):
    EmojiID: int
    KeyWords: Hashable
    EmojiPath: str


class _SimpleMainMissionConfig(TypedDict):
    MainMissionID: int
    Name: Hashable
    Type: int


class MessageType(int, Enum):
    Characters = 1
    """Character messages"""
    Others = 2
    """NPC messages"""
    GroupChats = 3
    """Group chat messages"""


class MessageCamp(int, Enum):
    AstralExpress = 1
    """Astral Express"""
    HertaSpace = 2
    """Herta Space Station"""
    JariloVI = 3
    """Jarilo-VI"""
    XianzhouLoufu = 4
    """Xianzhou Loufu"""
    StellaronHunters = 5
    """Stellaron Hunters"""
    IPC = 6
    """Interastral Peace Corporation"""
    Others = 99
    """Other camps"""


class MessageSender(str, Enum):
    Player = "Player"
    """Send manually by player by selecting an option."""
    PlayerAuto = "PlayerAuto"
    """Automatically sent by the game as a player's response to a message."""
    NPC = "NPC"
    """The NPC sends the message."""
    System = "System"
    """System message."""


class MessageItemType(str, Enum):
    Text = "Text"
    """Text message."""
    Image = "Image"
    """Image message."""
    Sticker = "Sticker"
    """Sticker message."""
    Raid = "Raid"
    """Raid message."""


class MissionType(str, Enum):
    MainQuest = "Main"
    # Gold quest
    DailyQuest = "Daily"
    # Green quest
    SideQuest = "Branch"
    # Blue quest
    CompanionQuest = "Companion"
    # Purple quest


class Text(Struct, tag=True):
    id: int
    """:class:`int`: The text ID."""
    section_id: int = field(name="sectionId")
    """:class:`int`: The text group ID."""
    sender_id: int | None = field(name="senderId")
    """:class:`int` | :class:`None`: The sender ID."""
    text: str
    """:class:`str`: The text content."""
    option: str | None
    """:class:`str` | :class:`None`: The option text content."""
    next_ids: list[int] = field(name="nextIds")
    """:class:`list[int]`: The next message ID."""
    kind: MessageSender

    @classmethod
    def from_config(cls: type[Text], config: _MessageItemConfig, contact_id: int, lang: str = "en") -> Text:
        option_str: str | None = get_hash_content_with(config["OptionText"], lang)
        if not option_str:
            option_str = None

        if "ContactsID" not in config and config["Sender"] == "NPC":
            config["ContactsID"] = contact_id
        elif "ContactsID" not in config:
            config["ContactsID"] = None

        return cls(
            id=config["ID"],
            section_id=config["SectionID"],
            sender_id=config["ContactsID"],
            text=get_hash_content_with(config["MainText"], lang),
            option=option_str,
            next_ids=config["NextItemIDList"],
            kind=MessageSender(config["Sender"]),
        )


class ImageInfo(Struct):
    id: int
    """:class:`int`: The image ID."""
    path: str
    """:class:`str`: The image path."""


class Image(Text, tag=True):
    image: ImageInfo
    """:class:`ImageInfo`: The image info."""

    @classmethod
    def from_config(
        cls: type[Image], config: _MessageItemConfig, contact_id: int, image: ImageInfo, lang: str = "en"
    ) -> Image:
        option_str: str | None = get_hash_content_with(config["OptionText"], lang)
        if not option_str:
            option_str = None

        if "ContactsID" not in config and config["Sender"] == "NPC":
            config["ContactsID"] = contact_id
        elif "ContactsID" not in config:
            config["ContactsID"] = None

        image.path = remap_icon_or_image(image.path)

        return cls(
            id=config["ID"],
            section_id=config["SectionID"],
            sender_id=config["ContactsID"],
            text=get_hash_content_with(config["MainText"], lang),
            option=option_str,
            next_ids=config["NextItemIDList"],
            kind=MessageSender(config["Sender"]),
            image=image,
        )


class StickerInfo(Struct):
    id: int
    """:class:`int`: The sticker ID."""
    path: str
    """:class:`str`: The sticker path."""
    keywords: str
    """:class:`str`: The sticker keywords."""

    @classmethod
    def from_config(cls: type[StickerInfo], config: _SimpleEmojiConfig, lang: str = "en") -> StickerInfo:
        return cls(
            id=config["EmojiID"],
            path=remap_icon_or_image(config["EmojiPath"]),
            keywords=get_hash_content_with(config["KeyWords"], lang),
        )


class Sticker(Text, tag=True):
    sticker: StickerInfo
    """:class:`StickerInfo`: The sticker info."""

    @classmethod
    def from_config(
        cls: type[Sticker], config: _MessageItemConfig, contact_id: int, sticker: StickerInfo, lang: str = "en"
    ) -> Sticker:
        option_str: str | None = get_hash_content_with(config["OptionText"], lang)
        if not option_str:
            option_str = None

        if "ContactsID" not in config and config["Sender"] == "NPC":
            config["ContactsID"] = contact_id
        elif "ContactsID" not in config:
            config["ContactsID"] = None

        return cls(
            id=config["ID"],
            section_id=config["SectionID"],
            sender_id=config["ContactsID"],
            text=get_hash_content_with(config["MainText"], lang),
            option=option_str,
            next_ids=config["NextItemIDList"],
            kind=MessageSender(config["Sender"]),
            sticker=sticker,
        )


class RaidInfo(Struct):
    id: int
    """:class:`int`: The raid ID."""
    name: str
    """:class:`str`: The raid name."""
    desc: str
    """:class:`str`: The raid description."""
    image: str
    """:class:`str`: The raid image path."""


class Raid(Text, tag=True):
    raid: RaidInfo
    """:class:`RaidInfo`: The raid info."""

    @classmethod
    def from_config(
        cls: type[Raid], config: _MessageItemConfig, contact_id: int, raid: RaidInfo, lang: str = "en"
    ) -> Raid:
        option_str: str | None = get_hash_content_with(config["OptionText"], lang)
        if not option_str:
            option_str = None

        if "ContactsID" not in config and config["Sender"] == "NPC":
            config["ContactsID"] = contact_id
        elif "ContactsID" not in config:
            config["ContactsID"] = None

        raid.image = remap_icon_or_image(raid.image)

        return cls(
            id=config["ID"],
            section_id=config["SectionID"],
            sender_id=config["ContactsID"],
            text=get_hash_content_with(config["MainText"], lang),
            option=option_str,
            next_ids=config["NextItemIDList"],
            kind=MessageSender(config["Sender"]),
            raid=raid,
        )


MessageContent = Text | Image | Sticker | Raid


class Message(Struct, tag=True):
    id: int
    """:class:`int`: The message section ID."""
    start_ids: list[int] = field(name="startIds")
    """:class:`int`: The start message IDs."""
    messages: dict[str, MessageContent]


class MissionInfo(Struct):
    id: int
    """:class:`int`: The mission ID."""
    name: str
    """:class:`str`: The mission name."""
    type: MissionType
    """:class:`MissionType`: The mission type."""

    @classmethod
    def from_config(cls: type[MissionInfo], config: _SimpleMainMissionConfig, lang: str = "en") -> MissionInfo:
        return cls(
            id=config["MainMissionID"],
            name=get_hash_content_with(config["Name"], lang),
            type=MissionType(config["Type"]),
        )


class MissionMessage(Message, tag=True):
    mission: MissionInfo
    """:class:`MissionInfo`: The mission info."""


MessageSectionType = Message | MissionMessage


class MessageContact(Struct):
    id: int
    """:class:`int`: The message contact ID."""
    name: str
    """:class:`str`: The message contact name."""
    signature: str | None
    """:class:`str` | :class:`None`: The message contact signature."""
    icon_url: str = field(name="iconPath")
    """:class:`str`: The message contact icon URL."""
    type: MessageType | None
    """:class:`MessageType`: The message contact type."""
    camp: MessageCamp | None
    """:class:`MessageCamp`: The message contact camp."""

    @classmethod
    def from_config(cls: type[MessageContact], config: _MessageContactsConfig, lang: str = "en") -> MessageContact:
        signature: str | None = get_hash_content_with(config["SignatureText"], lang)
        if not signature:
            signature = None
        contact_type = None
        if "ContactsType" in config:
            contact_type = MessageType(config["ContactsType"])
        contact_camp = None
        if "ContactsCamp" in config:
            contact_camp = MessageCamp(config["ContactsCamp"])
        return cls(
            id=config["ID"],
            name=get_hash_content_with(config["Name"], lang),
            signature=signature,
            icon_url=remap_icon_or_image(config["IconPath"]),
            type=contact_type,
            camp=contact_camp,
        )


class MessageGroup(Struct):
    id: int
    """:class:`int`: The message contact ID."""
    sections: list[list[MessageSectionType]]
    """:class:`list[list[MessageSectionType]]`: The message section IDs."""
    info: MessageContact
    """:class:`MessageContact`: The message contact info."""


def orjson_extend(obj: object) -> object:
    if isinstance(obj, Struct):
        return orjson.loads(msgspec.json.encode(obj))
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def save_config_xgen(name: str, config: dict[str, Any] | Struct) -> None:
    gen_dir = ROOT_DIR / "generated"

    if not name.endswith(".json"):
        name += ".json"

    fp_path = gen_dir / name
    fp_path.parent.mkdir(exist_ok=True, parents=True)
    with fp_path.open("wb") as fp:
        if isinstance(config, Struct):
            fp.write(msgspec.json.format(msgspec.json.encode(config), indent=2))
        else:
            fp.write(orjson.dumps(config, option=orjson.OPT_INDENT_2, default=orjson_extend))


def process_message_chains(
    start_id: int,
    contact_id: int,
    all_messages: dict[str, MessageContent],
    *,
    messages_configs: dict[str, _MessageItemConfig],
    item_images_config: dict[str, _MessageItemImageConfig],
    emoji_configs: dict[str, _SimpleEmojiConfig],
    message_raid_configs: dict[str, _MessageItemRaidEntranceConfig],
    raid_configs: dict[str, dict[Literal["0"], _SimpleRaidConfig]],
):
    message_info = messages_configs[str(start_id)]
    match message_info["ItemType"]:
        case "Text":
            msg = Text.from_config(message_info, contact_id)
        case "Image":
            img_raw = item_images_config[str(message_info["ItemContentID"])]
            img_inf = ImageInfo(
                id=img_raw["ID"],
                path=img_raw["ImagePath"],
            )
            msg = Image.from_config(message_info, contact_id, img_inf)
        case "Sticker":
            stick_raw = emoji_configs[str(message_info["ItemContentID"])]
            stick_inf = StickerInfo.from_config(stick_raw)
            msg = Sticker.from_config(message_info, contact_id, stick_inf)
        case "Raid":
            msg_raid_raw = message_raid_configs[str(message_info["ID"])]
            raid_raw = raid_configs[str(msg_raid_raw["RaidID"])]["0"]
            raid_inf = RaidInfo(
                id=raid_raw["RaidID"],
                name=get_hash_content_with(raid_raw["RaidName"]),
                desc=get_hash_content_with(raid_raw["RaidDesc"]),
                image=msg_raid_raw["ImagePath"],
            )
            msg = Raid.from_config(message_info, contact_id, raid_inf)
    all_messages[str(msg.id)] = msg
    if not msg.next_ids:
        return all_messages

    for next_id in msg.next_ids:
        process_message_chains(
            next_id,
            contact_id,
            all_messages,
            messages_configs=messages_configs,
            item_images_config=item_images_config,
            emoji_configs=emoji_configs,
            message_raid_configs=message_raid_configs,
            raid_configs=raid_configs,
        )


def main_loader():
    print("Getting configs...")
    emoji_configs = read_config("EmojiConfig", type=_SimpleEmojiConfig)
    message_raid_configs = read_config("MessageItemRaidEntrance", type=_MessageItemRaidEntranceConfig)
    raid_configs = cast(
        dict[str, dict[Literal["0"], _SimpleRaidConfig]], read_config("RaidConfig", type=_SimpleRaidConfig)
    )
    mission_configs = read_config("MainMission", type=_SimpleMainMissionConfig)
    item_images_config: dict[str, _MessageItemImageConfig] = read_config(
        "MessageItemImage", type=_MessageItemImageConfig
    )

    # Message contents
    messages_configs = read_config("MessageItemConfig", type=_MessageItemConfig)
    # The message chat sections
    message_sections = read_config("MessageSectionConfig", type=_MessageSectionConfig)
    # The message chat grouping
    message_groups = read_config("MessageGroupConfig", type=_MessageGroupConfig)

    message_contacts = read_config("MessageContactsConfig", type=_MessageContactsConfig)

    print("Processing contacts...")
    MSG_CONTACTS: dict[str, MessageContact] = {}
    for message_contact in message_contacts.values():
        try:
            msg_contact = MessageContact.from_config(message_contact)
            MSG_CONTACTS[str(message_contact["ID"])] = msg_contact
        except KeyError as err:
            print("  ", err, message_contact["ID"])

    save_config_xgen("message_contacts", MSG_CONTACTS)

    print("Preprocessing messages...")
    GROUPED_MESSAGES: dict[int, list[int]] = {}
    for message_group in message_groups.values():
        GROUPED_MESSAGES.setdefault(message_group["MessageContactsID"], []).append(message_group["ID"])

    GROUP_TOTAL = len(GROUPED_MESSAGES)
    print(f"Processing |{GROUP_TOTAL}| messages...")

    counter = 1
    USED_MAIN_CONTACTS = {}
    for group_contact_id, group_msg_ids in GROUPED_MESSAGES.items():
        group_msg = MessageGroup(
            id=group_contact_id,
            sections=[],
            info=MSG_CONTACTS[str(group_contact_id)],
        )
        USED_MAIN_CONTACTS[str(group_contact_id)] = group_msg.info

        for group_msg_id in group_msg_ids:
            raw_group = message_groups[str(group_msg_id)]
            if len(raw_group["MessageSectionIDList"]) > 1:
                print("  Group has more than 1 section...", group_contact_id, f"| {counter}/{GROUP_TOTAL}")
            current_sections: list[MessageSectionType] = []
            for section_id in raw_group["MessageSectionIDList"]:
                raw_section = message_sections[str(section_id)]
                if "MainMissionLink" in raw_section:
                    mission_raw = mission_configs[str(raw_section["MainMissionLink"])]
                    section_message = MissionMessage(
                        id=raw_section["ID"],
                        start_ids=raw_section["StartMessageItemIDList"],
                        messages={},
                        mission=MissionInfo.from_config(mission_raw),
                    )
                else:
                    section_message = Message(
                        id=raw_section["ID"],
                        start_ids=raw_section["StartMessageItemIDList"],
                        messages={},
                    )

                all_messages = {}
                for start_id in raw_section["StartMessageItemIDList"]:
                    print("  Processing message...", group_contact_id, start_id, f"| {counter}/{GROUP_TOTAL}")
                    process_message_chains(
                        start_id,
                        group_contact_id,
                        all_messages,
                        messages_configs=messages_configs,
                        item_images_config=item_images_config,
                        emoji_configs=emoji_configs,
                        message_raid_configs=message_raid_configs,
                        raid_configs=raid_configs,
                    )
                print(
                    "   Done processing message...",
                    group_contact_id,
                    start_id,
                    len(all_messages),
                    f"| {counter}/{GROUP_TOTAL}",
                )
                section_message.messages.update(all_messages)
                current_sections.append(section_message)
            group_msg.sections.append(current_sections)

        print(" Writing messages...", group_contact_id, f"| {counter}/{GROUP_TOTAL}")
        save_config_xgen(f"messages/{group_contact_id}", group_msg)
        counter += 1

    print("Saving all messages interactions...")
    save_config_xgen("messages", USED_MAIN_CONTACTS)


if __name__ == "__main__":
    print("Loading lang assets...")
    LANG_ASSETS = load_all_languages()
    get_hash_content_with = functools.partial(get_hash_content, lang_assets=LANG_ASSETS)
    main_loader()
