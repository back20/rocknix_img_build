import sys
import xml.etree.ElementTree as ET

def main(core_desc_path, xml_path):
    try:
        # 解析 XML 文件
        tree = ET.parse(xml_path)
    except ET.ParseError as e:
        print(f"[ERROR] XML 解析失败：{e}")
        sys.exit(1)
    except IOError as e:
        print(f"[ERROR] 无法打开 XML 文件 {xml_path}：{e}")
        sys.exit(1)
    root = tree.getroot()

    try:
        # 读取 core_desc.txt 文件
        with open(core_desc_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue

                # 解析字段
                parts = [p.strip() for p in line.split(',')]
                if len(parts) not in (3, 4):
                    print(f"[WARNING] 第 {line_num} 行格式错误：{line}")
                    continue
                system_name, emulator_name, core_name, *flags = parts
                is_default = 'default' in flags

                # 查找 system
                found_system = False
                target_system = None
                for system in root.findall('system'):
                    sys_name = system.find('name')
                    if sys_name is not None and sys_name.text.strip() == system_name.strip():
                        found_system = True
                        target_system = system
                        break

                if not found_system:
                    print(f"[ERROR] 第 {line_num} 行：未找到系统 {system_name}，退出。")
                    sys.exit(1)

                # 处理 emulators（自动创建）
                emulators = target_system.find('emulators')
                if emulators is None:
                    emulators = ET.Element('emulators')
                    emulators.tail = '\n'  # 保持原有格式
                    target_system.append(emulators)

                # 处理 emulator（自动创建）
                found_emulator = False
                target_emulator = None
                for emulator in emulators.findall('emulator'):
                    if emulator.get('name') == emulator_name:
                        found_emulator = True
                        target_emulator = emulator
                        break

                if not found_emulator:
                    target_emulator = ET.Element('emulator', {'name': emulator_name})
                    target_emulator.tail = '\n\t'  # 2 tabs
                    emulators.append(target_emulator)

                # 处理 cores（自动创建）
                cores = target_emulator.find('cores')
                if cores is None:
                    cores = ET.Element('cores')
                    cores.tail = '\n\t\t'  # 3 tabs
                    target_emulator.append(cores)

                # 如果是 default 核心，移除所有 old default
                if is_default:
                    for core in cores.findall('core'):
                        if core.get('default') == 'true':
                            del core.attrib['default']
                            core.tail = core.tail or ''

                # 添加新的 core
                new_core = ET.Element('core')
                new_core.text = core_name
                new_core.tail = '\n\t\t\t'  # 4 tabs

                if is_default:
                    new_core.set('default', 'true')

                if cores:
                    last_child = cores[-1]
                    last_child.tail = '\n\t\t\t'  # 4 tabs

                cores.append(new_core)

    except IOError as e:
        print(f"[ERROR] 无法读取 {core_desc_path}：{e}")
        sys.exit(1)

    try:
        # 写回 XML 文件
        tree.write(xml_path, encoding='UTF-8', xml_declaration=True)
        print("[INFO] XML 文件已更新。")
    except IOError as e:
        print(f"[ERROR] 写入 XML 文件失败：{e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法：add_core_to_emulator.py core_desc.txt es_systems.cfg")
        sys.exit(1)
    core_desc_path = sys.argv[1]
    xml_path = sys.argv[2]
    main(core_desc_path, xml_path)