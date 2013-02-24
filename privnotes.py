# coding=utf-8
'''
@name     PrivateNotes
@package  sublime_plugin
@author   Anton Shevchenko aka sancoder
@requires OpenSSL
'''

import sublime, sublime_plugin, os
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT

def settings():
    #should be read from settings, like this
    #ret = sublime.load_settings("PrivateNotes.sublime-settings")
    ret = {}
    # hint: don't use '~' symbol on Mac OS X as this will create directory named '~' !
    ret['notes_dir']   = u'/Users/anton/Dropbox/private-notes/'
    ret['password']    = u'the-password-you-should-set-up'
    ret['encoding']    = 'utf-8'
    ret['cipher']      = '-aes128'
    ret['openssl_cmd'] = 'openssl'
    ret['save_set_readonly'] = False
    return ret

# author of the functions panel and crypto is Derek Anderson (got from Crypto plugin)
#
# Encrypt/Decrypt using OpenSSL -aes128 and -base64
# EG similar to running this CLI command:
#   echo "data" | openssl enc -e -aes128 -base64 -pass "pass:lolcats"
#
#
# Create a new output panel, insert the message and show it
#
def panel(window, message):
    p = window.get_output_panel('crypto_error')
    p_edit = p.begin_edit()
    p.insert(p_edit, p.size(), message)
    p.end_edit(p_edit)
    p.show(p.size())
    window.run_command("show_panel", {"panel": "output.crypto_error"})

def crypto(view, enc_flag, password_param, data):
    openssl_cmd = settings().get('openssl_cmd')
    openssl_normpath = os.path.normpath(openssl_cmd)
    password_opt = "pass:%s" % password_param

    try:
        cipher_opt = settings().get('cipher')
        openssl = Popen([openssl_normpath, "enc", enc_flag, cipher_opt, \
            "-base64", "-pass", password_opt], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        openssl.stdin.write( data.encode("utf-8") )
        result, error = openssl.communicate()
    except OSError,e:
        error_message = """
            Please verify that you have installed OpenSSL.
            Attempting to execute: %s
            Error: %s
            """ % (openssl_normpath, e[1])
        panel(view.window(), error_message)
        return False

    # probably a wrong password
    if error:
        _err = error.splitlines()[0]
        if _err.find('unknown option') != -1:
            panel(view.window(), 'Error: ' + _err)
        elif _err.find("WARNING:") != -1:
            # skip WARNING's
            return result
        else:
            panel(view.window(), 'Error: Not encrypted or wrong password?')
        return False

    return result

#
def is_note_in_the_dir(fname):
    notes_dir = settings().get('notes_dir')
    return fname[:len(notes_dir)] == notes_dir

class InsertCurrentDateTimeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pos = self.view.sel()[0].begin()
        msg = datetime.now().strftime("%Y-%m-%d %H:%M:%S\n")
        self.view.insert(edit, pos, msg)

#opens a new note, with the timestamp in file_name and in the first line
class NewNoteWithTimestampCommand(sublime_plugin.WindowCommand):
    def run(self):
        now = datetime.now()
        v = self.window.new_file()
        notes_localdir = settings().get('notes_dir')
        notes_fulldir = notes_localdir + now.strftime("/%Y/%m-%d/")
        if not os.path.exists(notes_fulldir):
            os.makedirs(notes_fulldir)
        fname = now.strftime("%Y-%m-%d %H-%M-%S.txt")
        v.set_name(fname)
        v.settings().set('default_dir', notes_fulldir)
        v.run_command("insert_snippet", {"contents": fname + '\n\n'})

#encrypts note without first line
class EncryptNoteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        #whole buffer without first line
        start_pos = self.view.full_line(0).end()
        view_size = self.view.size()
        region = sublime.Region(start_pos, view_size)

        data = self.view.substr(region)
        password = settings().get('password')
        result = crypto(self.view, '-e', password, data)  
        if result:
            self.view.replace(edit, region, result)
        pass

#decrypts note without first line
class DecryptNoteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        #whole buffer without first line
        start_pos = self.view.full_line(0).end()
        view_size = self.view.size()
        region = sublime.Region(start_pos, view_size)

        data = self.view.substr(region)
        password = settings().get('password')
        result = crypto(self.view, '-d', password, data)  
        if result:
            result = result.decode(settings().get('encoding'))
            self.view.replace(edit, region, result)
        pass


class EncryptOnSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        if is_note_in_the_dir(view.file_name()):
            view.set_read_only(False)
            view.run_command("encrypt_note")


class DecryptAfterSave(sublime_plugin.EventListener):
    def on_post_save(self, view):
        if is_note_in_the_dir(view.file_name()):
            view.run_command("decrypt_note")
            if settings().get('save_set_readonly'):
                view.set_read_only(True)

class DecryptOnLoad(sublime_plugin.EventListener):
    def on_load(self, view):
        if is_note_in_the_dir(view.file_name()):
            view.run_command("decrypt_note")
            #hack: we can't tell sublime to reset dirty flag and it will ask
            #      about saving changes if we try to close
            #anyway, this is not working
            #view.set_scratch(True)
            if settings().get('save_set_readonly'):
                view.set_read_only(True)
