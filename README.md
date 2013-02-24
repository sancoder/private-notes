Private Notes in Sublime Text
=============================

The plugin auto-encrypts all files in certain folder before saving.  
The author is using the plugin to synchronize private notes in a Dropbox subfolder.  
You set the default password in the settings along with the folder you want to be encrypted.  
Settings are not in Dropbox, so your credential information is not synced.  
It is your responsibility to specify the same password on all computers you're using.  
After specifying the folder and the password on all computers you can write and read private notes.

The plugin hooks on_pre_save and on_load events and does encryption/decryption on the fly.  
The side-effect is that after Cmd+S the file remains modified (because it is encrypted-saved-decrypted).

To specify hotkeys paste this into user's keymap

    { "keys": ["super+\\"], "command": "new_note_with_timestamp" },
    { "keys": ["ctrl+shift+t"], "command": "insert_current_date_time" },
    { "keys": ["ctrl+shift+e"], "command": "encrypt_note" },
    { "keys": ["ctrl+shift+d"], "command": "decrypt_note" }

To specify settings modify privnotes.py

    ret['notes_dir']   = u'/Users/your-login/Dropbox/private-notes/' # could contain unicode characters
    ret['password']    = u'the-password-you-should-set-up'           # could contain unicode characters
    ret['encoding']    = 'utf-8'
    ret['cipher']      = '-aes128'
    ret['openssl_cmd'] = 'openssl' # the path to openssl command if not in $PATH
    ret['save_set_readonly'] = False

TODO
----
1. Use sublime-settings instead of specifying in code.
2. Use package-level keymap.
3. Integrate into sublime menu.
4. Menu command to change the password (will re-encode all files with new password).
5. Somehow tell sublime it shouldn't ask about saving decoded file after viewing.

