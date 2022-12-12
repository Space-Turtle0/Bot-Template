from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import (
    Any,
    Awaitable,
    Callable,
    List,
    Union,
    TYPE_CHECKING,
)

import discord
from discord import ButtonStyle, SelectOption, ui
from dotenv import load_dotenv
from github import Github

from core.logging_module import get_log

if TYPE_CHECKING:
    pass

load_dotenv()

# Module Variables
CoroutineType = Callable[[Any, Any], Awaitable[Any]]
github_client = Github(os.getenv("GH_TOKEN"))
_log = get_log(__name__)


def get_extensions():
    extensions = ["jishaku"]
    if sys.platform == "win32" or sys.platform == "cygwin":
        dirpath = "\\"
    else:
        dirpath = "/"

    for file in Path("utils").glob("**/*.py"):
        if "!" in file.name or "DEV" in file.name or "view_models" in file.name:
            continue
        extensions.append(str(file).replace(dirpath, ".").replace(".py", ""))
    return extensions


class SelectMenuHandler(ui.Select):
    """Adds a SelectMenu to a specific message and returns it's value when option selected.
    Usage:
        To do something after the callback function is invoked (the button is pressed), you have to pass a
        coroutine to the class. IMPORTANT: The coroutine has to take two arguments (discord.Interaction, discord.View)
        to work.
    """

    def __init__(
        self,
        options: List[SelectOption],
        custom_id: Union[str, None] = None,
        place_holder: Union[str, None] = None,
        max_values: int = 1,
        min_values: int = 1,
        disabled: bool = False,
        select_user: Union[discord.Member, discord.User, None] = None,
        roles: List[discord.Role] = None,
        interaction_message: Union[str, None] = None,
        ephemeral: bool = True,
        coroutine: CoroutineType = None,
        view_response=None,
        modal_response=None,
    ):
        """
        Parameters:
            options: List of discord.SelectOption
            custom_id: Custom ID of the view. Default to None.
            place_holder: Placeholder string for the view. Default to None.
            max_values Maximum values that are selectable. Default to 1.
            min_values: Minimum values that are selectable. Default to 1.
            disabled: Whenever the button is disabled or not. Default to False.
            select_user: The user that can perform this action, leave blank for everyone. Defaults to None.
            interaction_message: The response message when pressing on a selection. Default to None.
            ephemeral: Whenever the response message should only be visible for the select_user or not. Default to True.
            coroutine: A coroutine that gets invoked after the button is pressed. If None is passed, the view is stopped after the button is pressed. Default to None.
            view_response: The response of the view. Default to None.
            modal_response: The response of the modal. Default to None.
        """

        self.options_ = options
        self.custom_id_ = custom_id
        self.select_user = select_user
        self.roles = roles
        self.disabled_ = disabled
        self.placeholder_ = place_holder
        self.max_values_ = max_values
        self.min_values_ = min_values
        self.interaction_message_ = interaction_message
        self.ephemeral_ = ephemeral
        self.coroutine = coroutine
        self.view_response = view_response
        self.modal_response = modal_response

        if self.custom_id_:
            super().__init__(
                options=self.options_,
                placeholder=self.placeholder_,
                custom_id=self.custom_id_,
                disabled=self.disabled_,
                max_values=self.max_values_,
                min_values=self.min_values_,
            )
        else:
            super().__init__(
                options=self.options_,
                placeholder=self.placeholder_,
                disabled=self.disabled_,
                max_values=self.max_values_,
                min_values=self.min_values_,
            )

    async def callback(self, interaction: discord.Interaction):
        if self.select_user in [None, interaction.user] or any(
            role in interaction.user.roles for role in self.roles
        ):

            self.view.value = self.values[0]
            self.view_response = self.values[0]

            if self.modal_response:
                await interaction.response.send_modal(self.modal_response)

            elif self.interaction_message_:
                await interaction.response.send_message(
                    content=self.interaction_message_, ephemeral=self.ephemeral_
                )

            if self.coroutine is not None:
                await self.coroutine(interaction, self.view)
            else:
                self.view.stop()
        else:
            await interaction.response.send_message(
                content="You're not allowed to interact with that!", ephemeral=True
            )


class ButtonHandler(ui.Button):
    """
    Adds a Button to a specific message and returns it's value when pressed.
    Usage:
        To do something after the callback function is invoked (the button is pressed), you have to pass a
        coroutine to the class. IMPORTANT: The coroutine has to take two arguments (discord.Interaction, discord.View)
        to work.
    """

    def __init__(
        self,
        style: ButtonStyle,
        label: str,
        custom_id: Union[str, None] = None,
        emoji: Union[str, None] = None,
        url: Union[str, None] = None,
        disabled: bool = False,
        button_user: Union[discord.Member, discord.User, None] = None,
        roles: List[discord.Role] = None,
        interaction_message: Union[str, None] = None,
        ephemeral: bool = True,
        coroutine: CoroutineType = None,
        view_response=None,
    ):
        """
        Parameters:
            style: Label for the button
            label: Custom ID that represents this button. Default to None.
            custom_id: Style for this button. Default to None.
            emoji: An emoji for this button. Default to None.
            url: A URL for this button. Default to None.
            disabled: Whenever the button should be disabled or not. Default to False.
            button_user: The user that can perform this action, leave blank for everyone. Defaults to None.
            roles: The roles which the user needs to be able to click the button.
            interaction_message: The response message when pressing on a selection. Default to None.
            ephemeral: Whenever the response message should only be visible for the select_user or not. Default to True.
            coroutine: A coroutine that gets invoked after the button is pressed. If None is passed, the view is stopped after the button is pressed. Default to None.
        """
        self.style_ = style
        self.label_ = label
        self.custom_id_ = custom_id
        self.emoji_ = emoji
        self.url_ = url
        self.disabled_ = disabled
        self.button_user = button_user
        self.roles = roles
        self.interaction_message_ = interaction_message
        self.ephemeral_ = ephemeral
        self.coroutine = coroutine
        self.view_response = view_response

        if self.custom_id_:
            super().__init__(
                style=self.style_,
                label=self.label_,
                custom_id=self.custom_id_,
                emoji=self.emoji_,
                url=self.url_,
                disabled=self.disabled_,
            )
        else:
            super().__init__(
                style=self.style_,
                label=self.label_,
                emoji=self.emoji_,
                url=self.url_,
                disabled=self.disabled_,
            )

    async def callback(self, interaction: discord.Interaction):
        if self.button_user in [None, interaction.user] or any(
            role in interaction.user.roles for role in self.roles
        ):
            if self.custom_id_ is None:
                self.view.value = self.label_
                self.view_response = self.label_
            else:
                self.view.value = self.custom_id_
                self.view_response = self.custom_id_

            if self.interaction_message_:
                await interaction.response.send_message(
                    content=self.interaction_message_, ephemeral=self.ephemeral_
                )

            if self.coroutine is not None:
                await self.coroutine(interaction, self.view)
            else:
                self.view.stop()
        else:
            await interaction.response.send_message(
                content="You're not allowed to interact with that!", ephemeral=True
            )


def string_time_convert(string: str):
    """
    Filters out the different time units from a string (e.g. from '2d 4h 6m 7s') and returns a ``dict``.
    NOTE: The sequence of the time units doesn't matter. Could also be '6m 2d 7s 4h'.
    Params:
        string: The string which should get converted to the time units. (e.g. '2d 4h 6m 7s')
    Returns: A ``dict`` which the keys are 'days', 'hours', 'minutes', 'seconds' and the value is either a ``int`` or ``None``.
    """

    time_dict: dict = {}

    days = re.search("\d+d", string)
    hours = re.search("\d+h", string)
    minutes = re.search("\d+m", string)
    seconds = re.search("\d+s", string)

    if days is not None:
        time_dict["days"] = int(days.group(0).strip("d"))
    else:
        time_dict["days"] = None

    if hours is not None:
        time_dict["hours"] = int(hours.group(0).strip("h"))
    else:
        time_dict["hours"] = None

    if minutes is not None:
        time_dict["minutes"] = int(minutes.group(0).strip("m"))
    else:
        time_dict["minutes"] = None

    if seconds is not None:
        time_dict["seconds"] = int(seconds.group(0).strip("s"))
    else:
        time_dict["seconds"] = None

    return time_dict


class ConsoleColors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Colors:
    """
    Colors for the bot. Can be custom hex colors or built-in colors.
    """

    # *** Standard Colors ***
    blurple = discord.Color.blurple()
    green = discord.Color.brand_green()
    yellow = discord.Color.yellow()
    fuchsia = discord.Color.fuchsia()
    red = discord.Color.brand_red()

    # *** Hex Colors ***
    orange = 0xFCBA03
    dark_gray = 0x2F3136
    light_purple = 0xD6B4E8
    mod_blurple = 0x4DBEFF
    ss_blurple = 0x7080FA


class Others:
    """
    Other things to use for the bot. (Images, characters, etc.)
    """

    space_character = "　"