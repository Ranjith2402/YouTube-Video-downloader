import os
import random
import re
import ssl
import time
import webbrowser
import kivy.core.window
import pytube
import exceptions_handler
import pytube.extract
import http.client
import urllib.error
from typing import Union
from threading import Thread
from data_handler import DataLoader
from VideoDownloader import Downloader
from kivy.clock import Clock
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.toast import toast
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import Screen
from kivy.factory import Factory
from kivymd.uix.navigationdrawer.navigationdrawer import MDNavigationLayout
from kivy.utils import platform
from kivymd.uix.list.list import OneLineIconListItem, IconLeftWidget
# from kivy.core.window import EventLoop
from kivy.core.clipboard import Clipboard
from kivymd.uix.label import MDLabel

if platform == 'android':
    # jnius is not supported windows
    from AudioPlayer import AudioPlayer
else:
    from AudioPlayer import _AudioPlayer as AudioPlayer

ssl._create_default_https_context = ssl.SSLContext

Builder.load_string("""
#: import MDDialog kivymd.uix.dialog
#: import MDTopAppBar kivymd.uix.toolbar


<MyPopUp@MDDialog>:
    title: 'error'
    text: 'No internet'
    BoxLayout:
        orientation: "vertical"
        padding: 10
        # MDLabel:
        #     id: message
        #     text: "No Internet!!!"
        #     color: 1, 0.1, 0.5
        MDFlatButton:
            id: button
            text: "close"
            on_release: root.dismiss()
            size_hint_x: .8
            pos_hint: {"center_x": 0.5}
#___________________________ENDS__________________________________

<Reporter@Popup>:
    size_hint_y: None
    height: cm(5)
    title: 'Error detected!!!'
    BoxLayout:
        orientation: 'vertical'
        size_hint_Y: None
        height: self.minimum_height
        MDLabel:
            color: app.theme_cls.primary_light
            text: 'App closed unexpectedly/An error detected. Please share this file with developer to solve this issue'
        MDBoxLayout:
            MDRectangleFlatIconButton:
                id: check
                icon: 'checkbox-blank-circle-outline'
                text: 'delete this log file'
                on_release:
                    self.icon = 'checkbox-blank-circle-outline' if self.icon == 'checkbox-marked-circle-outline' else 'checkbox-marked-circle-outline'
        MDBoxLayout:
            spacing: "10dp"
            MDRaisedButton:
                text: 'send now'
                size_hint_x: 0.5
                on_release:
                    app.send_log_file(delete_log=(check.icon == 'checkbox-marked-circle-outline'))
                    root.dismiss()
            MDRectangleFlatButton:
                text: 'dismiss'
                on_release:
                    root.dismiss()
                    app.send_log_file(delete_log=(check.icon == 'checkbox-marked-circle-outline'), send=False)
                pos_hint: {"center_x": 0.5}
                texture_color: app.theme_cls.bg_normal
                size_hint_x: 0.5


<LogIn@Popup>:
    title: "User not verified"
    size_hint_y: None
    height: cm(4.5)
    BoxLayout:
        orientation: "vertical"
        MDLabel:
            id: message
            text: "It seems like you are not verified, Ask developer to verify you"
            pos_hint: {'top': 1}
            color: 1, 0.1, 0.5
        BoxLayout:
            MDRaisedButton:
                id: button_1
                text: "verify now"
                # on_release: app.login()
                pos_hint: {"center_x": 0.5}
                size_hint_x: 0.5
            MDRectangleFlatButton:
                id: button_2
                text: "dismiss"
                on_release: root.dismiss()
                pos_hint: {"center_x": 0.5}
                texture_color: app.theme_cls.bg_normal
                size_hint_x: 0.5


<NavigationDrawerItem@MDNavigationDrawerItem>:
    on_release: self.parent.parent.parent.set_state('close')
    icon_color: app.theme_cls.primary_light
    text_color: app.theme_cls.opposite_bg_light if app.theme_cls.theme_style == "Light" else app.theme_cls.opposite_bg_dark
    selected_color: app.theme_cls.primary_color


<MyNavigationDrawerItem@MDNavigationDrawer>:
    MDNavigationDrawerMenu:
        radius: (0, 16, 16, 0)
        MDNavigationDrawerHeader:
            title: "Youtube"
            text: "Video downloader"
            spacing: "4dp"
            padding: "12dp" , 0, 0, "56dp"
        MDNavigationDrawerLabel:
            text: "Downloaded items"
        NavigationDrawerItem:
            icon: "video"
            text: "Videos"
            on_release: app.showcase('movies')
        NavigationDrawerItem:
            icon: "music"
            text: "Music"
            # on_release: app.goto_videos()
            on_release: app.showcase("music")

        MDNavigationDrawerDivider:
        NavigationDrawerItem:
            icon: "hand-heart"
            text: "Support developer"
        NavigationDrawerItem:
            icon: "send"
            text: "Send feedback"

        MDNavigationDrawerDivider:
        MDNavigationDrawerLabel:
            text: 'Other'
        NavigationDrawerItem:
            icon: 'alert'
            text: 'Error Log'
            on_release: app.showcase('error log')
        
        # MDNavigationDrawerDivider:
        NavigationDrawerItem:
            icon: 'help-circle'
            text: 'Help'


<HomeToolBar>:
    MDScreenManager:
        MDScreen:
            MDTopAppBar:
                id: top_app_bar
                type_height: "large"
                title: "Youtube video downloader"
                elevation: 3
                pos_hint: {"top": 1}
                left_action_items: [["menu", lambda x: nav_bar.set_state("open")]]

    MyNavigationDrawerItem:
        swipe_edge_width: '25dp'
        id: nav_bar



<AllToolBar>:
    MDScreenManager:
        MDScreen:
            MDTopAppBar:
                id: top_app_bar
                type_height: "large"
                title: "Youtube video downloader"
                elevation: 3
                pos_hint: {"top": 1}
                left_action_items: [["arrow-left", lambda x: app.back()], ["menu", lambda x: nav_bar.set_state("open")]]

    MyNavigationDrawerItem:
        swipe_edge_width: '25dp'
        id: nav_bar


<HomeScreen>:
    MDScreen:
        MDFloatingActionButtonSpeedDial:
            data: app.fab_data
            callback: app.fab_callback
            root_button_anim: True

        MDRectangleFlatIconButton:
            id: logo
            text: "YouTube"
            icon_size: dp(50)
            font_size: 0.0664599025254763 * root.height
            icon: "youtube"
            icon_color: "red"
            line_color: app.theme_cls.bg_normal
            pos_hint: {"center_x": 0.5, "top": 0.88}
            on_press: app.toast("Made by Ranjith", tap=True)
        MDLabel:
            text: 'video downloader'
            font_size: dp(12)
            pos_hint: {'top': logo.y / root.height + 0.51, 'center_x': 0.505}
            halign: 'center'


        MDTextField:
            id: link
            icon_left: 'youtube'
            hint_text: "Your search query"
            size_hint: 0.85, None
            pos_hint: {"center_x": 0.5, "top": 0.75}
            on_focus:
                search.text = "search"
                search.icon = 'search-web'

        MDRoundFlatIconButton:
            id: search
            icon: 'search-web'
            text: "search"
            # elevation: 4
            pos_hint: {"center_x": 0.5, "top": root.ids.link.y / root.height - 0.01}
            on_release: root.search()

        MDLabel:
            id: random_stuff
            color: app.theme_cls.primary_color
            halign: 'center'
            pos_hint: {'center_x': 0.5, 'center_y': 0.4}
#___________________________________ENDS_____________________________________


<SettingsScreen>:
    ScrollView:
        BoxLayout:
            orientation: "vertical"
            spacing: dp(50)
            padding: 10
            size_hint_y: None
            height: self.minimum_height
            # MDRaisedButton:
            #     id: 'picker'
            #     text: 'choose color'
            #     pos_hint: {'right': 0.98, 'center_y':0.9}
            #     on_release: root.select_color()
            BoxLayout:  # <--- do not remove this, this is to give space for 1st widget
            BoxLayout:
                size_hint_y: None
                height: self.minimum_height
                MDLabel:
                    text: 'App theme    '
                    halign: 'right'
                MDIconButton:
                    icon: 'theme-light-dark'
                    on_release: app.change_theme()
            GridLayout:
                rows: 1
                size_hint_y: None
                height: self.minimum_height
                MDLabel:
                    text: 'Choose color palette     '
                    halign: 'right'
                    valign: 'center'
                Spinner:
                    id: spinner_pick
                    size_hint: None, None
                    background_normal: ''
                    height: dp(40)
                    width: dp(100)
                    background_color: app.theme_cls.primary_color
                    # height: self.texture_size[1] + 20
                    # width: self.texture_size[0] + 50
                    pos_hint: {'top': 0.9, 'right': 0.98}
                    values: 'Red', 'Pink', 'Purple', 'DeepPurple', 'Indigo', 'Blue', 'LightBlue', 'Cyan', 'Teal', 'Green', 'LightGreen', 'Lime', 'Yellow', 'Amber', 'Orange', 'DeepOrange', 'Brown', 'Gray', 'BlueGray'
                    on_text: root.set_color(self.text)

            BoxLayout:
                # pos_hint: {'top': 1 - spinner_pick.y / root.width }
                size_hint_y: None
                height: self.minimum_height
                padding: cm(0.3)
                MDLabel:
                    text: "Block \'HINDI\'    "
                    halign: "right"
                MDSwitch:
                    id: is_banned
                    pos_hint: {"right": 0.95, "center_y": 0.5}
                    on_active: root.toggle_language()

            MDBoxLayout:
                size_hint_y: None
                height: self.minimum_height
                MDLabel:
                    text: 'Number of results      '
                    valign: 'center'
                    halign: 'right'
                BoxLayout:
                    orientation: 'vertical'
                    size_hint: None, None
                    height: self.minimum_height
                    width: self.minimum_width
                    MDIconButton:
                        icon: 'arrow-up-drop-circle-outline'
                        on_release: root.change(1)
                        icon_size: dp(35)
                    MDLabel:
                        id: count
                        text: '1'
                        halign: 'center'
                    MDIconButton:
                        icon: 'arrow-down-drop-circle-outline'
                        on_release: root.change(-1)
                        icon_size: dp(35)

            BoxLayout:
                # pos_hint: {'top': 1 - spinner_pick.y / root.width }
                size_hint_y: None
                height: self.minimum_height
                padding: cm(0.3)
                MDLabel:
                    text: "Auto Download screen    "
                    halign: "right"
                MDSwitch:
                    id: auto_download
                    pos_hint: {"right": 0.95, "center_y": 0.5}
                    on_active: root.toggle_auto_download()

            BoxLayout:
                # pos_hint: {'top': 1 - spinner_pick.y / root.width }
                size_hint_y: None
                height: self.minimum_height
                padding: cm(0.3)
                MDLabel:
                    text: "Follow system theme    "
                    halign: "right"
                MDSwitch:
                    id: sys_theme
                    pos_hint: {"right": 0.95, "center_y": 0.5}
                    on_active: root.toggle_sys_theme()

    # AllToolBar:

#______________________________Ends____________________________________

<LoadingScreen>:
    MDScreen:
        MDProgressBar:
            id: progress
            pos_hint: {"center_y": 0.92}
        MDLabel:
            text: 'Loading...'
            halign: 'center'
            pos_hint: {"center_y": 0.5}
#__________________________________Ends__________________________________________


<ResultScreen>:
    BoxLayout:
        orientation: "vertical"
        BoxLayout:
            size_hint_y: None
            height: '70dp'
        ScrollView:
            id: scroll_layout
            BoxLayout:
                id: container
                size_hint_y: None
                height: self.minimum_height
                orientation: "vertical"
                spacing: cm(1.5)
    # ToolBar:

#_________________________________________Ends____________________________________________________

<DownLoadScreen>:
    #MDScreen:
    BoxLayout:
        orientation: 'vertical'
        # size_hint_y: None
        # height: '70dp'
        BoxLayout:  # this is to give top padding
            size_hint_y: None
            height: '70dp'
        ScrollView:
            do_scroll_x: False
            #always_overscroll: False
            BoxLayout:
                id: layout
                orientation: "vertical"
                spacing: 50
                padding: 10
                size_hint_y: None
                height: self.minimum_height
                BoxLayout:
                    id: thumbnail
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: 10
                    orientation: "vertical"
    
                BoxLayout:
                    id: vid_q
                    size_hint_y: None
                    height: self.minimum_height
                    MDLabel:
                        text: " Video Quality    "
                        halign: "right"
                    Spinner:
                        id: spinner
                        size_hint: None, None
                        background_normal: ''
                        height: dp(40)
                        width: dp(100)
                        # pos_hint: {'center_y': 0.5}
                        background_color: app.theme_cls.primary_color
                        values: '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p'
                        on_text: root.set_quality(self.text)
                BoxLayout:
                    id: only_vid_q
                    size_hint_y: None
                    height: self.minimum_height
                    MDLabel:
                        text: "Download video Only    "
                        halign: "right"
                    MDSwitch:
                        id: isVideo
                        pos_hint: {"right": 0.95, "center_y": 0.5}
                        on_active: root.disable_video(video_only=True)
    
                    MDLabel:
                        text: " only video    "
                        halign: "right"
                    Spinner:
                        id: spinner_video_only
                        disabled: True
                        size_hint: None, None
                        background_normal: ''
                        height: dp(40)
                        width: dp(100)
                        background_color: app.theme_cls.primary_color
                        pos_hint: {'center_y': 0.5}
                        values: '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p'
                        on_text: root.set_quality(self.text, video_only=True)
    
                # BoxLayout:
                #     id: aud_q
                #     MDLabel:
                #         text: "Audio Bit-rate    "
                #         halign: "right"
                #     Spinner:
                #         id: spinner2
                #         size_hint: None, None
                #         size: 100, 50
                #         pos_hint: {'center_y': 0.5}
                #         values: '320kbps', '128kbps', '64kbps'
                #         on_text: root.set_aud_quality(self.text)
    
                BoxLayout:
                    id: audio
                    size_hint_y: None
                    height: self.minimum_height
                    padding: cm(0.3)
                    MDLabel:
                        text: " audio bit-rate    "
                        halign: "right"
                    Spinner:
                        disabled: True
                        id: spinner_audio_only
                        size_hint: None, None
                        background_normal: ''
                        height: dp(40)
                        width: dp(100)
                        pos_hint: {'center_y': 0.5}
                        background_color: app.theme_cls.primary_color
                        values: '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p'
                        on_text: root.set_quality(self.text, audio_only=True)
                    MDLabel:
                        text: "Download audio Only    "
                        halign: "right"
                    MDSwitch:
                        id: isAudio
                        pos_hint: {"right": 0.95, "center_y": 0.5}
                        on_active: root.disable_video()
    
                BoxLayout:
                    MDProgressBar:
                        # size_hint: 0.9, None
                        id: download_progress
                    MDLabel:
                        id: download_percentage
                        text: ''
                        size_hint_x: None
                        halign: 'center'
                        # width: self.texture_size[0] + 10
    
                MDRoundFlatIconButton:
                    id: download_button
                    icon: "download"
                    text: "Download"
                    on_press: root.download()
                    pos_hint: {"center_x": 0.5, "y": 0.01}
    
                MDRoundFlatIconButton:
                    id: watch_button
                    icon: "youtube"
                    text: "watch on YouTube"
                    on_press: root.goto_youtube()
                    pos_hint: {"center_x": 0.5, "y": 0.01}

#___________________________________Ends__________________________________________


<SpinnerScreen>:
    MDScreen:
        MDSpinner:
            # this suppose to be work but it\'s not
            size_hint: None, None
            width: '1.5cm'
            pos_hint: {'center_x': 0.5, 'center_y': 0.4}
        MDLabel:
            text: 'loading all info please wait...\\n(this may take a while)\\nDO NOT CLOSE THIS'
            halign: 'center'
            pos_hint: {'center_y': 0.6}
#______________________________ENDS_________________________________________


<MyLabel@MDLabel>:
    size_hint_y: None
    height: self.texture_size[1]
    halign: 'center'

<Disclaimer>:
    MDScreen:
        ScrollView:
            BoxLayout:
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                padding: 25
                MyLabel:
                    text: 'DISCLAIMER'
                    font_style: 'H4'
                MyLabel:
                    text: '\\nLast updated November 20, 2022\\n'
                MyLabel:
                    text: '•WEBSITE DISCLAIMER:'
                    font_style: 'H5'
                    halign: 'left'
                MyLabel:
                    pos_hint: {'center_x': 0.55}
                    size_hint_x: 0.92
                    halign: 'left'
                    text: '\\n      The information provided by YoutubeVideoDownloader ("we," "us," or "our") on our mobile application is for general informational purposes. All information on our mobile application is provided in good faith, however we make no representation or warranty of any kind, express or implied, regarding the accuracy, adequacy, validity, reliability, availability, or completeness of any information on our mobile application. UNDER NO CIRCUMSTANCE SHALL WE HAVE ANY LIABILITY TO YOU FOR ANY LOSS OR DAMAGE OF ANY KIND INCURRED AS A RESULT OF THE USE OF OUR MOBILE APPLICATION OR RELIANCE ON ANY INFORMATION PROVIDED ON OUR MOBILE APPLICATION. YOUR USE OF OUR MOBILE APPLICATION AND YOUR RELIANCE ON ANY INFORMATION ON OUR MOBILE APPLICATION IS SOLELY AT YOUR OWN RISK.\\n\\n'
                MyLabel:
                    text: '•EXTERNAL LINKS DISCLAIMER:'
                    font_style: 'H5'
                    halign: 'left'
                MyLabel:
                    pos_hint: {'center_x': 0.55}
                    size_hint_x: 0.92
                    halign: 'left'
                    text: '\\n      Our mobile application may contain (or you may be sent through our mobile application) links to other websites or content belonging to or originating from third parties (i.e; Youtube). Such external links are not investigated, monitored, or checked for accuracy, adequacy, validity, reliability, availability, or completeness by us. WE DO NOT WARRANT, ENDORSE, GUARANTEE, OR ASSUME RESPONSIBILITY FOR THE ACCURACY OR RELIABILITY OF ANY INFORMATION OFFERED BY THIRD-PARTY WEBSITES (here Youtube only) LINKED THROUGH THE SITE. WE WILL NOT BE A PARTY TO OR IN ANY WAY BE RESPONSIBLE FOR MONITORING ANY TRANSACTION BETWEEN YOU AND YOUTUBE PROVIDERS OF PRODUCTS OR SERVICES.\\n\\n'
                MyLabel:
                    text: '•Download NOTE:'
                    font_style: 'H5'
                    halign: 'left'
                MyLabel:
                    pos_hint: {'center_x': 0.55}
                    size_hint_x: 0.92
                    # halign: 'left'
                    text: '\\n      Downloading the copyrighted video/audio is illegal we were not responsible for your downloads!. Download at your risk\\n'
                MyLabel:
                    halign: 'left'
                    font_style: 'Caption'
                    text: '*By pressing Continue you agreed to the above conditions\\n'


                MDRaisedButton:
                    text: 'Continue'
                    on_release: root.agree()
                    pos_hint: {'center_x': 0.5}
                    size_hint: 0.6, None

                # BoxLayout
                #     size_hint_y: None
                #     height: self.minimum_height
                #     # pos_hint: {'center_x': 1}
                #     spacing: 10
                #     padding: 25
                    # MDRaisedButton:
                    #     text: 'Agree'
                    #     on_release: root.agree()
                    # MDRectangleFlatButton:
                    #     text: 'Reject'
                    #     on_release: root.reject()


#_____________________________________________________ENDS__________________________________________________________
<ShowCase>:
    BoxLayout:
        orientation: "vertical"
        BoxLayout:
            size_hint_y: None
            height: '70dp'
        RecycleView:
            id: scroll_layout
            MDBoxLayout:
                id: container
                size_hint_y: None
                height: self.minimum_height
                orientation: "vertical"
#____________________________ENDS_____________________________

<MediaPLayer>:
    MDScreen:
        canvas:
            Color:
                rgba: app.theme_cls.primary_light
            Rectangle:
                size: self.size
                pos: self.pos
        
        MDIconButton:
            icon: 'chevron-left'
            pos_hint: {'top': 1}
            id: navigate_up
            theme_icon_color: 'ContrastParentBackground'
            on_release: app.back()
        
        MDLabel:
            text: '...'
            id: song_name
            theme_text_color: 'ContrastParentBackground'
            pos_hint: {'top': 1.43, 'x':0.03}
        
        MDBoxLayout:
            size_hint: None, None
            pos_hint: {'center_x': 0.5, 'center_y':0.58}
            height: root.height * 0.6
            width: root.width * 0.8
            padding: 25
            canvas.after:
                Color:
                    rgba: 0, 0, 0, .7
                Line:
                    width: 2
                    rounded_rectangle: (self.x, self.y, self.right - self.x, self.top - self.y, 16)
                    # rgb: 1, 0, 1
                # Rectangle:
                #     size: self.size
                #     pos: self.pos
                
            Image:
                source: 'images/music-icon.png'
        
        MDBoxLayout:
            size_hint_y: None
            height: self.minimum_height + dp(25)
            pos_hint: {'y': control_panel.top / root.height + 0.1}
            MDLabel:
                id: curr_pos
                halign: 'center'
                # size_hint: None, None
                # width: self.texture_size[0]
                text: root.process_to_time(round(slider.value))
                color: 0, 0, 0, .85
            MDSlider:
                size_hint_x: None
                width: root.width * .75
                id: slider
                hint: False
                show_off: False
            MDLabel:
                # size_hint: None, None
                id: max_time
                text: '1:40'
                halign: 'center'
                color: 0, 0, 0, .85
        
        MDBoxLayout:
            id: control_panel
            size_hint: None, None
            width: self.minimum_width
            pos_hint: {'center_x': 0.5, 'y': 0.05}
            MDIconButton:
                icon_size: '25sp'
                theme_icon_color: 'ContrastParentBackground'
                icon: 'rewind-10'
                on_release: root.jump(True)
                pos_hint: {'center_y': 0.5}
            MDIconButton:
                icon_size: '50sp'
                theme_icon_color: 'ContrastParentBackground'
                icon: 'skip-previous'
                on_release: root.play_last()
                pos_hint: {'center_y': 0.5}
            MDIconButton:
                icon_size: '100dp'
                id: play
                theme_icon_color: 'ContrastParentBackground'
                icon: 'play'
                on_release: root.pause_play()
                pos_hint: {'center_y': 0.5}
            MDIconButton:
                icon_size: '50sp'
                theme_icon_color: 'ContrastParentBackground'
                icon: 'skip-next'
                on_release: root.play_next()
                pos_hint: {'center_y': 0.5}
            MDIconButton:
                icon_size: '25sp'
                theme_icon_color: 'ContrastParentBackground'
                icon: 'fast-forward-10'
                on_press: root.jump(False)
                pos_hint: {'center_y': 0.5}
    

""")

thumbnail_kvs = ["""
GridLayout:
    id: layout
    size_hint_y: None
    cols: 1
    height: self.minimum_height
    #orientation: "vertical"
    image: image.__self__
    AsyncImage:
        id: image
        size_hint_y: None
        keep_aspect: True
        # height: self.width * (9 / 16)
        # pos_hint: {"center_x": button.center_x, "center_y": button.center_y}
        on_load:
            self.parent.remove_widget(self)


    Button:
        size_hint_y: None
        id: button
        height: self.width * (9 / 16)
        texture_size: self.size
        texture: image.texture
        on_release: app.select(root)

    MDBoxLayout:
        size_hint_y: None
        height: self.minimum_height
        MDLabel:
            id: title
            size_hint_y: None
            height: self.texture_size[1]
            pos_hint: {'center_y': 0.5}
            # valign: "center"
            color: app.theme_cls.primary_color
        Label:
            id: time
            size_hint: None,None
            width: self.texture_size[0] + 10
            color: app.theme_cls.primary_dark
""",
                 """
BoxLayout:
    id: layout
    size_hint_y: None
    cols: 1
    height: self.minimum_height
    spacing: 15
    #orientation: "vertical"
    image: image.__self__
    AsyncImage:
        id: image
        # size_hint_y: None
        # height: self.width * (9 / 16)
        # pos_hint: {"center_x": button.center_x, "center_y": button.center_y}
        on_load: 
            self.parent.remove_widget(self)


    Button:
        size_hint_y: None
        id: button
        height: self.width * (9 / 16)
        texture_size: self.size
        texture: image.texture
        on_release: app.select(root)
    MDBoxLayout:
        # size_hint_y: None
        # height: self.minimum_height
        spacing: 10
        MDLabel:
            id: title
            size_hint_y: None
            height: self.texture_size[1]
            pos_hint: {'center_y': 0.5}
            valign: "center"
            color: app.theme_cls.primary_color
        Label:
            id: time
            size_hint: None,None
            valign: 'center'
            pos_hint: {'center_y': 0.5}
            width: self.texture_size[0] + 10
            color: app.theme_cls.primary_dark
"""]

data_engine = DataLoader()
json_error = False
try:
    data_engine.load()
    if data_engine.data == {}:
        json_error = True
        raise FileNotFoundError
except FileNotFoundError:
    data_engine.create()
    data_engine.load()

data_engine.cwd = os.getcwd()
previous_screen = current_screen = "home"

last_esc_down = tap_start_time = time.time()
tap_count = 0

random_text_home = ['Welcome to youtube video downloader',
                    'Made in Python Made by Ranjith',
                    'search search to search something',
                    'Do people really read this',
                    'Remember you are a beta tester for this app Beta builds are not final',
                    'Don\'t worry about crashes more crashes on Beta means less crashes later ;)',
                    'Do try any weird things on this app (I suggest) \nYou can try if you want',
                    'Found any BUG please report me, so I can fix it',
                    'Technically this app never crashes :)',
                    'This app is still under development, this is BETA version\nLMAO full version never comes i guess',
                    'Hmm',
                    'Report all issues to developer',
                    'Got a greate idea for this app!!! discuss with developer let\'s make it happen',
                    'Turn on auto download option on customise screen, just copy the link and download',
                    'This app is not capable of merging audio and video hence some qualities may not available with '
                    'audio',
                    'Music play-back system coming soon...']

auto_download = False
is_permission_allowed = False
blocked_l_tap_count = 0
last_link = ''

dialog1_message = ''
dialog1_text = ''
dialog2_dict = {}


def change_dir():
    if platform == 'android':
        output_path = '/storage/emulated/0/Youtube video downloader'
    else:
        output_path = 'C:\\users'
        fold = os.listdir(output_path)
        output_path += '\\' + fold[-1] + '\\music\\youtube_video_downloader'

    try:
        os.chdir(output_path)
    except FileNotFoundError:
        os.mkdir(output_path)
        os.chdir(output_path)


def permission_callback(*args):
    global is_permission_allowed
    for permission, state in zip(*args):
        if permission == 'WRITE_EXTERNAL_STORAGE' and state is True:
            change_dir()
            is_permission_allowed = True


def get_permissions(*_):
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE,
                         Permission.WRITE_EXTERNAL_STORAGE,
                         Permission.INTERNET,
                         Permission.ACCESS_NETWORK_STATE],
                        callback=permission_callback)


def convert_bytes(byte) -> str:
    if byte >= 1024 ** 3:
        return str(round(byte / (1024 ** 3), 2)) + "Gb"
    elif byte >= 1024 ** 2:
        return str(round(byte / (1024 ** 2), 2)) + "Mb"
    elif byte >= 1024:
        return str(round(byte / 1024, 2)) + "kb"
    else:
        return str(byte) + "bytes"


def normalise(t):
    t = round(t)
    d = t // (60 * 60 * 24)
    if d > 1:
        d = f"{d}days : "
    elif d == 1:
        d = f"{d}day : "
    else:
        d = ""
    t = t % (60 * 60 * 24)
    h = t // (60 * 60)
    if h or d:
        h = f"{d}{h}h : "
    else:
        h = ""
    t = t % (60 * 60)
    m = t // 60
    if m or h:
        m = f"{h}{m}m : "
    else:
        m = ""
    s = t % 60
    if s or m:
        s = f'{m}{s}s'
    else:
        s = '• Live'  # •৹
    return s


def login():
    pass


def check_is_banned(text):
    if data_engine.data['is_banned'] and (
            f'{chr(104)}{chr(105)}{chr(110)}{chr(100)}{chr(105)}' in text.lower() or re.search(r'[\u0900-\u097f]',
                                                                                               text)):
        return True
    return False


def dialog_type1(message='No internet connection!!!', button_text='close'):
    global dialog1_message, dialog1_text
    dialog1_message = message
    dialog1_text = button_text
    Clock.schedule_once(_dialog_type1, 0.3)


def _dialog_type1(_=None):
    window = Factory.MyPopUp()
    window.text = dialog1_message
    window.ids['button'].text = dialog1_text
    window.open()


def dialog_type2(message='Login',
                 button1='verify',
                 button2='dismiss',
                 title='Error',
                 on_press_button1=login,
                 on_press_button2=None):
    global dialog2_dict
    dialog2_dict = {'message': message,
                    'button1': button1,
                    'button2': button2,
                    'title': title,
                    'on_press_button1': on_press_button1,
                    'on_press_button2': on_press_button2}.copy()
    Clock.schedule_once(_dialog_type2, 0.3)


def _dialog_type2(_=None):
    window = Factory.LogIn()
    window.title = dialog2_dict['title']
    window.ids['message'].text = dialog2_dict['message']
    window.ids['button_1'].text = dialog2_dict['button1']
    window.ids['button_2'].text = dialog2_dict['button2']
    window.ids['button_1'].bind(on_release=dialog2_dict['on_press_button1'])
    if dialog2_dict['on_press_button2'] is not None:
        window.ids['button_2'].bind(on_release=dialog2_dict['on_press_button2'])
    window.ids['button_1'].bind(on_release=window.dismiss)
    # window.ids['message'].text = dialog2_dict['message']
    window.open()


def dialog_type3():
    window = Factory.Reporter()
    window.open()


def check_file_permission():
    if platform == 'android':
        try:
            os.listdir('/storage/emulated/0/')
            return True
        except PermissionError:
            return False
    elif platform == "win":
        return True


def check_system_theme() -> Union[str, None]:
    if platform == 'android':
        from kvdroid.tools import darkmode
        if not data_engine.data['follow system theme']:
            return None
        if darkmode.dark_mode():
            return "Dark"
        return 'Light'
    else:
        return None  # I think not needed


def minimised(*args):
    print(args)
    print('Minimised')


def maximised(*args):
    print(args)
    print('maximised')


def hook_keyboard(_, key, *__):
    global last_esc_down
    if key == 27:
        print('Esc button')
        print(previous_screen)
        if sm.current in ('home', 'disclaimer'):
            if time.time() - last_esc_down < 2:
                stop_app()
            app.toast('press again to exit')
            last_esc_down = time.time()
            return True
        elif sm.current in ('result', 'settings', 'loading'):
            set_current_screen('home')
            return True
        elif sm.current in ('download', 'spinner_screen'):
            if not download.is_downloading:
                if result.selected_widget is not None:  # this is made while developing this may not use full after making it an app
                    download.on_leave()
                    set_current_screen('result')
                else:
                    set_current_screen('home')
            else:
                app.toast('can\'t quit now please wait till download complete')
            return True
        elif sm.current == 'showcase':
            set_current_screen(previous_screen)
            return True
        elif sm.current == 'media_player':
            set_current_screen('showcase')
            return True
    elif key == 13 and sm.current == 'home':
        home.search()


def set_current_screen(screen):
    global current_screen
    current_screen = screen
    Clock.schedule_once(_set_screen, 0.1)


def _set_screen(_):
    global previous_screen
    if previous_screen != current_screen and sm.current not in ('spinner_screen', 'showcase', 'media_player'):
        previous_screen = sm.current
        # print("previous screen -->", previous_screen)
    sm.current = current_screen


def stop_app():
    app.on_stop()
    app.stop()


def regex_match_link(clip):
    if re.match(
            r'^((?:https?:)?//)?((?:www|m)\.)?(youtube(-nocookie)?\.com|youtu.be)(/(?:[\w\-]+\?v=|embed/|v/)?)([\w\-]+)(\S+)?$',
            clip):
        return True
    return False


def list_items(mode):
    if mode == "music":
        tmp = [i for i in os.listdir(f"./{mode}") if i.lower().endswith(('.mp3', '.wav', '.ogg'))]
    elif mode == 'movies':
        tmp = [i for i in os.listdir(f'./{mode}') if i.lower().endswith(('.mp4', '.3gpp'))]
    else:
        tmp = [i for i in os.listdir(f'./{mode}') if i.lower().endswith('.txt') and re.search(r'\(\d\).txt', i)]
    if not tmp:
        return None
    return tmp


class HomeToolBar(MDNavigationLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AllToolBar(MDNavigationLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class YouTube:
    def __init__(self, link):
        self.link = link
        self.loading = True
        self.is_error = False
        self.url = None
        self.thumbnail_url = None
        self.title = None
        self.length = None
        self.widget = None
        self.is_AgeRestricted = None
        self.is_private = None

    def create(self, _=None):
        self.is_error = False
        self.loading = True
        try:
            self.url = self.link.embed_url
            self.thumbnail_url = self.link.thumbnail_url
            self.title = self.link.title
            self.length = self.link.length
            self.widget = Builder.load_string(thumbnail_kvs[data_engine.data['ui_mode'] - 1])
            self.widget.ids['image'].source = self.thumbnail_url
            self.widget.ids['title'].text = self.title
            self.widget.ids['time'].text = normalise(self.length)
            watch_html = pytube.YouTube(self.url).watch_html
            self.is_AgeRestricted = pytube.extract.is_age_restricted(watch_html)
            if not self.length:
                self.widget.ids['time'].color = (1, 0, 0)
        except urllib.error.URLError:
            self.is_error = True
        except http.client.IncompleteRead:
            self.is_error = True
        except http.client.RemoteDisconnected:
            self.is_error = True
        except ConnectionAbortedError:
            self.is_error = True
        self.loading = False


class MediaPlayer(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_child = None
        self.do_update = True
        self.state = 'ready'
        self.is_playing = False
        self.audio_player = AudioPlayer()
        self.clock_event = Clock.schedule_interval(self.update, 1/62.5)  # 60fps 2.5 fps bonus (just kidding)

    def play(self, path, goto_screen=True):
        if self.last_child is not None:
            self.last_child.theme_text_color = "Primary"
        child = showcase.audio_items[path]
        child.theme_text_color = 'Custom'
        child.text_color = child.icon_color = app.theme_cls.colors[data_engine.data['color_pallet']]['A400']
        self.last_child = child
        self.audio_player.file_path = "music/" + path
        self.set_max_values()
        self.state = 'playing'
        self.ids['song_name'].text = path
        if not goto_screen:
            return
        set_current_screen('media_player')

    def pause_play(self):
        if self.audio_player.is_playing:
            self.ids['play'].icon = 'pause'
            self.audio_player.pause()
            self.state = 'paused'
        else:
            self.ids['play'].icon = 'play'
            self.audio_player.play()
            self.state = 'playing'

    def play_next(self):
        index = showcase.selected_index + 1
        if index >= len(showcase.audio_files):
            index = 0
        self.play(showcase.audio_files[index])
        showcase.selected_index = index

    def play_last(self):
        index = showcase.selected_index - 1
        if index < 0:
            index = len(showcase.audio_files) - 1
        self.play(showcase.audio_files[index])
        showcase.selected_index = index

    def seek(self, to):
        self.audio_player.seek(to)

    def set_max_values(self):
        val = int(self.audio_player.length / 1000)
        self.ids['slider'].max = val
        self.ids['max_time'].text = self.process_to_time(val)

    def update(self, _=None):
        if self.do_update:
            if self.ids['slider'].active:
                self.do_update = False
            elif not self.audio_player.is_playing and self.state not in ('ready', 'paused'):
                self.play_next()
                return
            self.ids['slider'].value = self.audio_player.current_pos / 1000
        else:
            if self.ids['slider'].active:
                return
            self.seek(self.ids['slider'].value * 1000)
            self.do_update = True

    def update_(self, value):
        self.ids['slider'].value = value

    def jump(self, is_backward):
        self.audio_player.jump_in_time(backward=is_backward)

    def process_to_time(self, val):
        h = val // 3600
        m = (val // 60) % 60
        s = val % 60
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"


class ShowCase(Screen):
    mode = None
    audio_items = {}
    audio_files = []
    selected_index = None

    def show(self, mode='music'):
        if sm.current == 'media_player':
            set_current_screen('show_case')
            return
        if sm.current == 'showcase':
            if mode == self.mode:
                return
            else:
                self.ids.container.clear_widgets()
        self.mode = mode
        Clock.schedule_once(self.load, 3)

    def load(self, _=None):
        # set_current_screen('showcase')
        items = list_items(self.mode)
        if items is None:
            if self.mode == 'error log':
                text = 'Hurray no error log found'
            elif self.mode == 'music':
                text = 'No audio downloaded yet'
            else:
                text = 'No videos downloaded yet'
            label = MDLabel(text=text)
            label.size_hint_y = None
            label.center_x = label.center_y = 0.5
            label.halign = label.valign = 'center'
            label.disabled = True
            self.ids.container.add_widget(label)
        elif self.mode == 'error log':
            for item in items:
                button = OneLineIconListItem(IconLeftWidget(icon='check-box'), text=item)  # can't create icon widget outside as it needs parent
                self.ids.container.add_widget(button)
        elif self.mode == 'music':
            for i in range(5):
                for item in items:
                    button = OneLineIconListItem(IconLeftWidget(icon='music'), text=item)
                    button.bind(on_release=self.play)
                    self.ids.container.add_widget(button)
                    self.audio_items[item] = button
                    self.audio_files.append(item)
                    time.sleep(1)
                    print('new item added', item)
                    # self.widgets.append(button)
        else:
            for item in items:
                button = OneLineIconListItem(IconLeftWidget(icon='movie'), text=item)
                self.ids.container.add_widget(button)
        # set_current_screen('showcase')

    def on_leave(self):
        while sm.current == 'showcase':
            time.sleep(0.016)
        if sm.current == 'media_player':
            return
        self.ids.container.clear_widgets()
        self.mode = None
        # self.widgets = []
        # self.clear_widgets()
        # self.add_widget(AllToolBar())

    def on_enter(self):
        if self.selected_index is not None:
            media_player.play(self.audio_files[self.selected_index], goto_screen=False)

    def play(self, button):
        media_player.play(button.text)
        self.selected_index = self.audio_files.index(button.text)


class DownloadedItems(Screen):
    def show(self, folder='Music'):
        pass


class SpinnerScreen(Screen):
    pass


class HomeScreen(Screen):
    isLoading = False

    def on_enter(self):
        self.ids['random_stuff'].text = random.choice(random_text_home)
        self.isLoading = False
        # toolbar.change()
        for i in self.ids:
            print(i)
        # self.ids['toolbar'].change()

    def search(self):
        text = self.ids['link'].text.strip()
        if text and not loading.isLoading and not self.isLoading:
            if regex_match_link(text) and text.endswith("?feature=share"):
                self.ids['link'].text = text[:-14]
            if not data_engine.data['isVerified']:
                Factory.LogIn().open()
                return
            self.isLoading = True
            result.load()
            set_current_screen("loading")
        # else:
        #     kivy.core.window.WindowBase().maximize()


class LoadingScreen(Screen):
    isLoading = False

    def on_leave(self):
        self.ids['progress'].value = 0

    def set_max(self, max_val):
        if max_val > 0:
            self.ids['progress'].max = max_val

    def update(self, value, duration=0.3):
        curr = int(self.ids['progress'].value)
        if value > curr:
            for val in range(curr * 10, value * 10 + 1):
                time.sleep(duration / ((value - curr) * 10))
                self.ids['progress'].value = val / 10
        else:
            self.ids['progress'].value = value


class ResultScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.selected_widget = None
        self.allow_once = False
        self.widgets = []
        self.links = []
        self.wid_link_pair = {}
        self.search_object = None
        self.loading_complete = False
        self.is_error = False
        self.result_slice = data_engine.data['result limit']

    def un_block_once(self, _):
        app.toast('unblocked for once')
        self.allow_once = True

    def select(self, link):
        global blocked_l_tap_count
        if check_is_banned(self.wid_link_pair[link].title) and not self.allow_once:
            app.toast('That language is blocked, you can turn on in customise screen')
            blocked_l_tap_count += 1
            if blocked_l_tap_count == 5:
                blocked_l_tap_count = 2
                dialog_type2('That video is blocked, you can unblock it on \'CUSTOMISE screen\'',
                             'Unblock once',
                             button2='keep blocking',
                             title='Video is bocked',
                             on_press_button1=self.un_block_once)
            return
        elif self.wid_link_pair[link].length == 0:
            app.toast('Can\'t download live video')
            return
        elif self.wid_link_pair[link].is_AgeRestricted:
            dialog_type1('This video is age restricted and may cause some errors, I\'m trying hard to fix this', 'ok')
            return

        self.allow_once = False
        self.ids.container.clear_widgets()
        self.selected_widget = self.wid_link_pair[link]
        self.ids['container'].remove_widget(self.selected_widget.widget)
        download.ids['thumbnail'].add_widget(self.selected_widget.widget)
        download.load()

    def add(self):
        if self.is_error:
            loading.set_max(20)
            loading.update(18, duration=0.2)
            set_current_screen("home")
            dialog_type1()
            print('current screen set')
            return
        if not self.links:
            dialog_type1("No results for found, try checking keywords")
            set_current_screen("home")
            return
        loading.set_max(len(self.links) + 1)
        loading.update(1)
        self.widgets = [].copy()
        self.wid_link_pair = {}.copy()
        error_count = 0
        for index, link in enumerate(self.links):
            widget = YouTube(link)
            Clock.schedule_once(widget.create, 0.3)
            loading.update(index + 2)
            while widget.loading:
                time.sleep(0.25)
            if widget.is_error:
                error_count += 1
                continue
            self.widgets.append(widget)
            self.wid_link_pair[widget.thumbnail_url] = widget
        if error_count >= len(self.links):
            dialog_type1('Something went wrong please try again')
            set_current_screen("home")
        if sm.current == 'loading':
            set_current_screen('result')
        result.ids['scroll_layout'].scroll_y = 1  # to always scroll to the top as new results were loaded

    def complete(self):
        print(sm.current)
        if sm.current == 'loading' or self.is_error:
            # checking is_error is needs since for no connection this
            # function is called before current still in home
            p = Thread(target=self.add, daemon=True)
            p.start()
            print('complete')

    def get_links(self):
        global auto_download
        self.loading_complete = False
        try:
            self.search_object = pytube.Search(home.ids['link'].text)
            self.links = self.search_object.results[:self.result_slice]
        except urllib.error.URLError:
            self.is_error = True
        except http.client.IncompleteRead:
            self.is_error = True
        except ConnectionAbortedError:
            self.is_error = True
        self.loading_complete = True
        self.complete()
        if len(self.links) == 1:
            auto_download = True
            app.toast('Only one result found auto selecting...')

    def load(self, _=None):
        self.is_error = False
        thread = Thread(target=self.get_links, daemon=True)
        thread.start()

    def on_enter(self):
        global auto_download
        self.ids.container.clear_widgets()
        for widget in self.widgets:
            self.ids.container.add_widget(widget.widget)
        if len(self.widgets) == 0:
            dialog_type1('something went wrong')
            set_current_screen('home')
            return
        if auto_download:
            auto_download = False
            try:
                for i in self.wid_link_pair:
                    self.select(i)
                    break
            except KeyError:
                pass

    def on_leave(self):
        global blocked_l_tap_count
        blocked_l_tap_count = 2 if blocked_l_tap_count == 2 else 0
        for wid in self.widgets:
            self.remove_widget(wid.widget)
            result.ids.container.remove_widget(wid.widget)
        result.ids.container.clear_widgets()
        self.ids.container.clear_widgets()


class DownloadScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.post_raise = False
        self.file_name = ''
        self.download_engine = None
        self.audio_only = False
        self.video_only = False
        self.loading = False
        self.is_downloading = False
        self.last_quality = self.quality = data_engine.data['previous_quality']

    def goto_youtube(self, _=None):
        webbrowser.open(self.download_engine.link)

    def disable_video(self, video_only=False):
        if video_only:
            self.ids['spinner'].disabled = not self.ids['spinner'].disabled
            self.ids['spinner_video_only'].disabled = not self.ids['spinner'].disabled
            self.quality = self.ids['spinner_video_only'].text if self.ids['spinner'].disabled else self.ids[
                'spinner'].text
        else:
            self.ids['vid_q'].disabled = not self.ids['vid_q'].disabled
            self.ids['only_vid_q'].disabled = self.ids['vid_q'].disabled
            self.audio_only = self.ids['vid_q'].disabled
            self.ids['spinner_audio_only'].disabled = not self.audio_only
            if self.ids['vid_q'].disabled:
                self.quality = self.ids['spinner_audio_only'].text
            else:
                self.ids['vid_q'].disabled = False
                self.ids['only_vid_q'].disabled = self.ids['vid_q'].disabled
                if self.ids['spinner'].disabled:
                    self.quality = self.ids['spinner_video_only'].text
                else:
                    self.quality = self.ids['spinner'].text
        self.set_filter()
        self.display_size()
        self.ids['download_button'].disabled = False

    def disable_all(self):
        # it is required while downloading something
        self.ids['vid_q'].disabled = True
        self.ids['only_vid_q'].disabled = True
        self.ids['audio'].disabled = True
        self.ids['download_button'].disabled = True

    def enable_all(self, _=None):
        if not self.ids['isAudio'].active:
            self.ids['vid_q'].disabled = False
            self.ids['only_vid_q'].disabled = False
        self.ids['audio'].disabled = False
        self.ids['download_button'].disabled = False

    def error_callback(self, msg):
        if msg == 'no connection-1a0':
            # dialog_type1()
            set_current_screen('result')
            # Clock.schedule_once(self.on_leave)
            return
        elif msg == 'no connection':
            dialog_type1()
        elif msg == 'poor connection':
            dialog_type1('Unable to complete download please check your internet connection')
        elif msg == 'something went wrong':
            dialog_type1('something went wrong, can\'t complete download try again')
        elif msg == 'something went wrong2':
            dialog_type1('Something went wrong try a different video quality')
            self.quality = self.last_quality
            if not self.audio_only:
                self.ids['spinner'].text = self.quality
            self.set_filter()
            self.display_size()
        elif msg == 'something went wrong3':
            dialog_type1(
                'sorry to say this, the selected video is not available this feature is still under development :(')
            set_current_screen('result')
            return
        elif msg == 'tier 3 age restriction':
            dialog_type2("Can't by pass age gate :(",
                         button1='continue to youtube',
                         on_press_button1=self.goto_youtube,
                         title='Age restriction')
            set_current_screen('result')
        elif msg == 'not available':
            app.toast(f'{self.quality} is not available')
            self.quality = self.download_engine.video_qualities[0]
            self.ids['spinner'].text = str(self.quality)
        elif msg == "file exists":
            dialog_type2("It seems this file already downloaded!!! (press any where out side to cancel download)",
                         button1='Rename',
                         button2='Download again',
                         title='File exists',
                         on_press_button1=self.rename_and_download,
                         on_press_button2=self.download_again)
        else:
            app.toast(msg)
        Clock.schedule_once(self.enable_all, 0.3)
        self.ids['download_progress'].value = 0
        self.ids['download_percentage'].text = ''
        self.display_size()
        self.is_downloading = False

    def toaster(self, _=None):
        app.toast(self.file_name + " is downloaded")

    def rename_and_download(self, _=None):
        self.download(ignore=True, rename=True)

    def download_again(self, _=None):
        self.download(ignore=True)

    def progress_callback(self, percentage):
        self.ids['download_progress'].value = int(percentage * 100)
        self.ids['download_percentage'].text = f'{int(percentage * 100)}%'

    def set_quality(self, quality, audio_only=False, video_only=False):
        if self.loading:
            return
        if video_only:
            self.video_only = True
            self.quality = quality
        elif audio_only:
            self.audio_only = True
            self.quality = quality
        else:
            self.audio_only = False
            self.video_only = False
        self.last_quality = self.quality
        self.quality = quality
        self.set_filter()
        self.display_size()
        self.ids['download_button'].disabled = False

    def set_filter(self):
        if self.download_engine is None:
            return
        self.download_engine.set_filter(res=self.quality, audio_only=self.audio_only, video_only=self.video_only)
        self.ids['download_progress'].value = 0
        self.ids['download_percentage'].text = ''
        if self.ids['spinner'].text not in self.download_engine.video_qualities and self.ids['spinner'].text != '':  # I don't know why I wrote this
            app.toast(self.ids['spinner'].text + ' is not available')
            self.ids['spinner'].text = self.download_engine.video_qualities[0]

    def display_size(self):
        if self.download_engine is not None:
            self.ids['download_button'].text = f'Download ({convert_bytes(self.download_engine.get_size)})'

    def load(self):
        set_current_screen('spinner_screen')
        thread = Thread(target=self.load_all_info, daemon=True)
        thread.start()

    def load_all_info(self, _=None):
        # remove this while making it an App
        self.loading = True
        if result.selected_widget is None:
            self.download_engine = Downloader('https://youtu.be/DkLHPm9NoZg',
                                              self.on_complete_callback,
                                              self.error_callback,
                                              progress=self.progress_callback)
        else:
            self.download_engine = Downloader(result.selected_widget.url,
                                              self.on_complete_callback,
                                              self.error_callback,
                                              progress=self.progress_callback)
        self.download_engine.check_available_quality()
        if self.download_engine.is_error:
            # this is needs to be in kivy main loop
            self.post_raise = True
        else:
            # since this creates graphics is needs to be in kivy main loop
            # the above code take too long to load all info
            # hence leading spinner_screen to stuck, so this makes process smoother
            Clock.schedule_once(self.post_process, 0.2)

    def post_process(self, _=None):
        if self.post_raise:
            self.post_raise = False
            dialog_type1()
            set_current_screen('result')
            return
        self.ids['spinner'].values = self.download_engine.video_qualities.copy()
        self.ids['spinner_video_only'].values = self.download_engine.video_only_qualities.copy()
        self.ids['spinner_audio_only'].values = self.download_engine.audio_qualities.copy()
        try:
            self.ids['spinner_video_only'].text = self.download_engine.video_only_qualities[-1]
            self.ids['spinner_audio_only'].text = self.download_engine.audio_qualities[
                -2]  # most of the time* 128kbps is at this index
        except IndexError:
            if not self.download_engine.audio_qualities:
                self.ids['spinner_audio_only'].values = []
            elif not self.download_engine.video_only_qualities:
                self.ids['spinner_video_only'].values = []
            else:
                self.ids[
                    'spinner_video_only'].values = self.download_engine.video_only_qualities if self.download_engine.video_only_qualities else []
                self.ids[
                    'spinner_audio_only'].values = self.download_engine.audio_qualities if self.download_engine.audio_qualities else []
        if self.download_engine.res is None:
            self.error_callback('something went wrong3')
            return
        self.set_filter()
        self.display_size()
        self.loading = False
        if sm.current == 'spinner_screen':
            set_current_screen('download')

    def download(self, ignore=False, rename=False):
        # Clock.schedule_once(self.download_engine.download, 1)
        if not check_file_permission():
            dialog_type2('In order to download videos File permission is required or else I can\'t help with this',
                         'Give permission',
                         on_press_button1=get_permissions,
                         title='Permission Error')
            return
        elif platform == 'android' and os.getcwd() != '/storage/emulated/0/Youtube video downloader':
            change_dir()
        if self.is_downloading:
            return
        thread = Thread(target=self.download_engine.download, args=(ignore, rename))
        self.disable_all()
        thread.start()
        self.ids['download_button'].text = 'Downloading...'
        app.toast('Download started')
        self.is_downloading = True
        self.progress_callback(0.01)

    def on_complete_callback(self, _, name):
        # Be care-full this is in a thread and cannot create graphics on outside the kivy thread
        self.file_name = name
        Clock.schedule_once(self.toaster, 0.2)  # since it is in a thread
        if not (self.audio_only or self.video_only):
            # print(self.audio_only, self.video_only)
            data_engine.data['previous_quality'] = self.quality
        Clock.schedule_once(self.enable_all, 0.3)  # this is not working without clock after kivymd==1.1.1
        # self.ids['download_progress'].value = 0
        # self.ids['download_percentage'].text = ''
        self.progress_callback(1)
        self.ids['download_button'].text = 'Downloaded :)'
        self.is_downloading = False
        data_engine.data['downloaded'].append(result.selected_widget.url)
        while len(data_engine.data['downloaded']) > 100:
            data_engine.data['downloaded'].pop(0)
        data_engine.save()

    def on_enter(self):
        # self.ids['thumbnail'].add_widget(result.selected_widget.widget)
        if result.selected_widget is None:
            self.load()
        self.ids['spinner'].text = data_engine.data['previous_quality']
        self.set_filter()
        self.display_size()

    def on_leave(self, _=None):
        self.ids['thumbnail'].remove_widget(result.selected_widget.widget)


class SettingsScreen(Screen):
    def toggle_auto_download(self):
        data_engine.data['auto download'] = self.ids['auto_download'].active
        data_engine.save()

    def toggle_language(self):
        # data_engine.data['is_banned'] = not data_engine.data['is_banned']
        data_engine.data['is_banned'] = self.ids['is_banned'].active
        data_engine.save()

    def toggle_sys_theme(self):
        data_engine.data['follow system theme'] = self.ids['sys_theme'].active
        data_engine.save()
        tmp = check_system_theme()
        if tmp is not None:
            app.theme_cls.theme_style = tmp

    def change(self, n):
        n = int(self.ids['count'].text) + n
        if n == 0 or n == 21:
            return
        self.ids['count'].text = str(n)
        data_engine.data['result limit'] = n
        result.result_slice = n

    def set_color(self, color):
        app.theme_cls.primary_palette = color
        data_engine.data['color_pallet'] = color

    def on_enter(self):
        self.ids['spinner_pick'].text = data_engine.data['color_pallet']
        self.ids['auto_download'].active = data_engine.data['auto download']
        self.ids['is_banned'].active = data_engine.data['is_banned']
        if platform == 'android':
            self.ids['sys_theme'].active = data_engine.data['follow system theme']
        else:
            self.ids['sys_theme'].disabled = True
        self.ids['count'].text = str(data_engine.data['result limit'])

    def on_leave(self):
        data_engine.data['color_pallet'] = self.ids['spinner_pick'].text
        data_engine.save()


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = ''
        self.last_tap_msg = ''
        self.last_toast_time = time.time()
        self.fab_data = {'Theme': 'theme-light-dark', 'Customise': 'cog', 'close': 'close-circle'}
        # self.fab_data = {"Theme": ["theme-light-dark",
        #                            'on_release', lambda x: self.change_theme()],
        #                  "Customise": ["cog",
        #                                'on_release', lambda x: set_current_screen('settings')],
        #                  "close": ["close-circle",
        #                            'on_release', lambda x: stop_app()]}

    def back(self):
        hook_keyboard(None, 27)

    def send_log_file(self, delete_log=False, send=True):

        print(os.getcwd())
        if send and platform == "android":
            from kvdroid.tools import share_files
            # TODO: file format is not practical
            share_files(os.getcwd() + "/error log/error.txt")
        if delete_log:
            # TODO: delete data file arises an error
            exceptions_handler.delete_log_file()

    def select(self, instance):
        if sm.current == 'result':
            result.select(instance.ids['image'].source)

    def goto_videos(self):
        set_current_screen('spinner_screen')

    def showcase(self, mode):
        # if sm.current == 'showcase' and showcase.mode != mode:
        #     set_current_screen(previous_screen)
        #     time.sleep(0.2)
        showcase.show(mode)
        set_current_screen('showcase')

    def fab_callback(self, instance):
        if instance.icon == "theme-light-dark":
            self.change_theme()
        elif instance.icon == "cog":
            set_current_screen('settings')
        elif instance.icon == "close-circle":
            stop_app()

    def _toast(self, _=None):
        toast(self.message)

    def toast(self, msg, tap=False, tap_c=3, tap_duration=1):
        global tap_start_time, tap_count
        if self.last_tap_msg == msg and time.time() - self.last_toast_time <= 2.3:
            return
        if not tap:
            self.message = msg
            self.last_toast_time = time.time()
            self.last_tap_msg = msg
            Clock.schedule_once(self._toast)
        if time.time() - tap_start_time <= tap_duration:
            tap_count += 1
            if tap_c == tap_count - 1:
                self.message = msg
                Clock.schedule_once(self._toast)
                self.last_toast_time = time.time()
                self.last_tap_msg = msg
                tap_count = 0
                tap_start_time = time.time()
        else:
            tap_count = 0
            tap_start_time = time.time()

    def change_theme(self):
        self.theme_cls.theme_style = "Light" if self.theme_cls.theme_style == "Dark" else "Dark"
        data_engine.data["theme"] = self.theme_cls.theme_style

    def build(self):
        return sm

    def on_start(self):
        global auto_download
        if json_error:
            self.toast('Something went!!! wrong data reset')
        if not data_engine.data['isAgree to T&C']:
            class Disclaimer(Screen):
                def agree(self):
                    set_current_screen('home')
                    data_engine.data['isAgree to T&C'] = True
                    data_engine.save()

                def reject(self):
                    app.toast('Agree to terms and conditions to use this app')
                    stop_app()

            sm.add_widget(Disclaimer(name='disclaimer'))
            set_current_screen('disclaimer')
        self.theme_cls.primary_palette = data_engine.data['color_pallet']
        kivy.core.window.EventLoop.window.bind(on_keyboard=hook_keyboard)
        # EventLoop.window.bind(on_keyboard=hook_keyboard,
        #                       on_maximize=maximised,
        #                       on_minimize=minimised)
        theme = check_system_theme()
        if theme is not None:
            self.theme_cls.theme_style = theme
        else:
            self.theme_cls.theme_style = data_engine.data['theme']

        if check_file_permission():
            change_dir()
            if exceptions_handler.check_log_file():
                dialog_type3()
        clip = Clipboard.paste()
        if regex_match_link(clip):
            home.ids['link'].text = clip
            home.ids['search'].text = 'Link that you copied'
            if clip in data_engine.data['downloaded'] or (
                    clip.endswith('?feature=share') and clip[:-14] in data_engine.data['downloaded']):
                self.toast('This video is already downloaded')
                home.ids['search'].text = "Already downloaded"
                home.ids['search'].icon = 'check-bold'
            elif data_engine.data['auto download']:
                if data_engine.data['last link'] != clip:
                    auto_download = True
                    data_engine.data['last link'] = clip
                    data_engine.save()
                    home.search()

    def on_stop(self):
        data_engine.save()


if __name__ == "__main__":
    app = MainApp()
    sm = MDScreenManager()
    home = HomeScreen(name="home")
    result = ResultScreen(name="result")
    loading = LoadingScreen(name='loading')
    settings = SettingsScreen(name='settings')
    download = DownloadScreen(name='download')
    spinner = SpinnerScreen(name='spinner_screen')
    showcase = ShowCase(name='showcase')
    media_player = MediaPlayer(name='media_player')

    home.add_widget(HomeToolBar())
    result.add_widget(AllToolBar())
    settings.add_widget(AllToolBar())
    download.add_widget(AllToolBar())
    showcase.add_widget(AllToolBar())

    sm.add_widget(home)
    sm.add_widget(result)
    sm.add_widget(loading)
    sm.add_widget(settings)
    sm.add_widget(download)
    sm.add_widget(spinner)
    sm.add_widget(showcase)
    sm.add_widget(media_player)

    # sm.current = 'media_player'
    # media_player.play('path/to/audio/file')
    # print(app.theme_cls.colors[data_engine.data['theme']])

    app.run()
