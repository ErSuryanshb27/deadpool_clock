[app]
title = Deadpool Clock
package.name = deadpoolclock
package.domain = org.deadpool
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav
version = 1.0
requirements = python3,kivy,plyer
orientation = portrait
fullscreen = 0
android.permissions = VIBRATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
