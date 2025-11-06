#!/usr/bin/env bash
# file: tests/test_cgroups.sh

./filter.sh cat <<'EOF'
noise line
@fname[3448510, 8]: /proc/self/task/943521/ns/net
@fname[3448555, 8]: /proc/self/task/943559/ns/net
@fname[3448594, 8]: /proc/self/task/943581/ns/net

@read_bytes[/etc/ld.so.cache]: 0
@read_bytes[/proc/self/task/943559/ns/net]: 0
@read_bytes[/dev/null]: 0
@read_bytes[/usr/bin/calico-node]: 0
@read_bytes[/proc/self/task/943521/ns/net]: 0
@read_bytes[/proc/self/task/943581/ns/net]: 0
@read_bytes[/sys/devices/system/cpu/possible]: 15
@read_bytes[/sys/devices/system/cpu/online]: 20
@read_bytes[/sys/kernel/mm/transparent_hugepage/hpage_pmd_size]: 24
@read_bytes[/etc/nsswitch.conf]: 216
@read_bytes[/etc/resolv.conf]: 297
@read_bytes[/etc/localtime]: 381
@read_bytes[/etc/hosts]: 813
@read_bytes[/lib64/libpthread.so.0]: 2496
@read_bytes[/lib64/libc.so.6]: 2592
@read_bytes[/lib64/libz.so.1]: 2688
@read_bytes[/lib64/libelf.so.1]: 2688
@read_count[/proc/self/task/943521/ns/net]: 2
@read_count[/proc/self/task/943581/ns/net]: 2
@read_count[/proc/self/task/943559/ns/net]: 2
@read_count[/etc/ld.so.cache]: 3
@read_count[/usr/bin/calico-node]: 3
@read_count[/dev/null]: 5
@read_count[/etc/nsswitch.conf]: 6
@read_count[/etc/resolv.conf]: 6
@read_count[/etc/localtime]: 6
@read_count[/sys/kernel/mm/transparent_hugepage/hpage_pmd_size]: 6
@read_count[/etc/hosts]: 6
@read_count[/sys/devices/system/cpu/possible]: 6
@read_count[/lib64/libpthread.so.0]: 6
@read_count[/sys/devices/system/cpu/online]: 7
@read_count[/lib64/libc.so.6]: 9
@read_count[/lib64/libz.so.1]: 12
@read_count[/lib64/libelf.so.1]: 12



@read_time[/proc/self/task/943559/ns/net]: 0
@read_time[/dev/null]: 0
@read_time[/usr/bin/calico-node]: 0
@read_time[/proc/self/task/943521/ns/net]: 0
@read_time[/proc/self/task/943581/ns/net]: 0
@read_time[/etc/ld.so.cache]: 0
@read_time[/etc/localtime]: 19601
@read_time[/lib64/libpthread.so.0]: 19821
@read_time[/etc/hosts]: 30737
@read_time[/sys/kernel/mm/transparent_hugepage/hpage_pmd_size]: 31988
@read_time[/lib64/libc.so.6]: 35561
@read_time[/etc/nsswitch.conf]: 39941
@read_time[/etc/resolv.conf]: 44545
@read_time[/lib64/libz.so.1]: 52043
@read_time[/sys/devices/system/cpu/possible]: 53996
@read_time[/lib64/libelf.so.1]: 68205
@read_time[/sys/devices/system/cpu/online]: 70365
@tracked_cgid: 9037
@tracked_comm: calico-node
@un_read_bytes[3448555, 5]: 1
@un_read_bytes[3448594, 5]: 1
@un_read_bytes[3448510, 5]: 1
@un_read_bytes[3783, 5]: 1
@un_read_bytes[3787, 0]: 3
@un_read_bytes[3783, 9]: 39
@un_read_bytes[3448510, 11]: 51
@un_read_bytes[3448594, 10]: 51
@un_read_bytes[3448510, 10]: 52
@un_read_bytes[3448594, 11]: 52
@un_read_bytes[3448594, 12]: 705
@un_read_bytes[3448510, 9]: 705
@un_read_bytes[3448555, 9]: 1146
@un_read_bytes[3787, 15]: 1208
@un_read_bytes[3787, 5]: 1256
@un_read_count[3448510, 9]: 1
@un_read_count[3448594, 12]: 1
@un_read_count[3448510, 10]: 1
@un_read_count[3448594, 11]: 1
@un_read_count[3448510, 11]: 1
@un_read_count[3448594, 5]: 1
@un_read_count[3783, 5]: 1
@un_read_count[3783, 9]: 1
@un_read_count[3448510, 5]: 1
@un_read_count[3448594, 10]: 1
@un_read_count[3448555, 5]: 1
@un_read_count[3787, 0]: 3
@un_read_count[3448555, 9]: 3
@un_read_count[3787, 15]: 4
@un_read_count[3787, 5]: 1256
@un_read_time[3783, 5]: 11398
@un_read_time[3448594, 10]: 13842
@un_read_time[3448510, 10]: 14114
@un_read_time[3448510, 11]: 15738
@un_read_time[3448510, 9]: 16596
@un_read_time[3448555, 5]: 17761
@un_read_time[3448594, 5]: 17849
@un_read_time[3448510, 5]: 19193
@un_read_time[3448594, 11]: 23308
@un_read_time[3448594, 12]: 23905
@un_read_time[3783, 9]: 25442
@un_read_time[3448555, 9]: 69240
@un_read_time[3787, 15]: 97447
@un_read_time[3787, 5]: 13978391
@un_read_time[3787, 0]: 36282157238
@un_write_bytes[3448555, 6]: 1
@un_write_bytes[3448510, 6]: 1
@un_write_bytes[3783, 6]: 1
@un_write_bytes[3448594, 6]: 1
@un_write_bytes[3787, 0]: 2
@un_write_bytes[3783, 9]: 39
@un_write_bytes[3448510, 9]: 103
@un_write_bytes[3448594, 12]: 103
@un_write_bytes[3448555, 1]: 111
@un_write_bytes[3448555, 9]: 119
@un_write_bytes[3787, 6]: 1264
@un_write_bytes[3787, 15]: 2115
@un_write_count[3448555, 6]: 1
@un_write_count[3448510, 9]: 1
@un_write_count[3783, 9]: 1
@un_write_count[3448594, 12]: 1
@un_write_count[3448510, 6]: 1
@un_write_count[3448555, 1]: 1
@un_write_count[3783, 6]: 1
@un_write_count[3448594, 6]: 1
@un_write_count[3448555, 9]: 2
@un_write_count[3787, 0]: 2
@un_write_count[3787, 15]: 3
@un_write_count[3787, 6]: 1264
@un_write_time[3448555, 6]: 16654
@un_write_time[3783, 6]: 16779
@un_write_time[3448510, 6]: 21939
@un_write_time[3448555, 1]: 25570
@un_write_time[3448594, 6]: 38200
@un_write_time[3783, 9]: 87211
@un_write_time[3448510, 9]: 133040
@un_write_time[3448594, 12]: 171098
@un_write_time[3448555, 9]: 183495
@un_write_time[3787, 15]: 400138
@un_write_time[3787, 6]: 19406612
@un_write_time[3787, 0]: 24318528661
@write_bytes[/lib64/libelf.so.1]: 0
@write_bytes[/sys/devices/system/cpu/online]: 0
@write_bytes[/etc/localtime]: 0
@write_bytes[/proc/self/task/943521/ns/net]: 0
@write_bytes[/etc/resolv.conf]: 0
@write_bytes[/proc/self/task/943581/ns/net]: 0
@write_bytes[/sys/devices/system/cpu/possible]: 0
@write_bytes[/lib64/libpthread.so.0]: 0
@write_bytes[/lib64/libc.so.6]: 0
@write_bytes[/etc/nsswitch.conf]: 0
@write_bytes[/etc/hosts]: 0
@write_bytes[/usr/bin/calico-node]: 0
@write_bytes[/lib64/libz.so.1]: 0
@write_bytes[/sys/kernel/mm/transparent_hugepage/hpage_pmd_size]: 0
@write_bytes[/etc/ld.so.cache]: 0
@write_bytes[/proc/self/task/943559/ns/net]: 0
@write_bytes[/dev/null]: 0
@write_count[/proc/self/task/943559/ns/net]: 2
@write_count[/proc/self/task/943581/ns/net]: 2
@write_count[/proc/self/task/943521/ns/net]: 2
@write_count[/sys/kernel/mm/transparent_hugepage/hpage_pmd_size]: 3
@write_count[/etc/nsswitch.conf]: 3
@write_count[/etc/ld.so.cache]: 3
@write_count[/etc/hosts]: 3
@write_count[/lib64/libelf.so.1]: 3
@write_count[/lib64/libc.so.6]: 3
@write_count[/etc/resolv.conf]: 3
@write_count[/lib64/libpthread.so.0]: 3
@write_count[/etc/localtime]: 3
@write_count[/usr/bin/calico-node]: 3
@write_count[/lib64/libz.so.1]: 3
@write_count[/sys/devices/system/cpu/online]: 3
@write_count[/sys/devices/system/cpu/possible]: 3
@write_count[/dev/null]: 5



@write_time[/etc/localtime]: 0
@write_time[/etc/resolv.conf]: 0
@write_time[/etc/nsswitch.conf]: 0
@write_time[/proc/self/task/943521/ns/net]: 0
@write_time[/sys/devices/system/cpu/possible]: 0
@write_time[/etc/ld.so.cache]: 0
@write_time[/proc/self/task/943559/ns/net]: 0
@write_time[/usr/bin/calico-node]: 0
@write_time[/sys/kernel/mm/transparent_hugepage/hpage_pmd_size]: 0
@write_time[/lib64/libelf.so.1]: 0
@write_time[/etc/hosts]: 0
@write_time[/lib64/libz.so.1]: 0
@write_time[/lib64/libc.so.6]: 0
@write_time[/lib64/libpthread.so.0]: 0
@write_time[/dev/null]: 0
@write_time[/proc/self/task/943581/ns/net]: 0
@write_time[/sys/devices/system/cpu/online]: 0
EOF
