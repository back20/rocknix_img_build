import sys
import xml.etree.ElementTree as ET

def main(ext_desc_path, xml_path):
    try:
        # 解析 XML 文件
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"[ERROR] XML 解析失败：{e}")
        sys.exit(1)
    except IOError as e:
        print(f"[ERROR] 无法打开 XML 文件 {xml_path}：{e}")
        sys.exit(1)

    try:
        # 构建 system_name -> system_node 映射
        system_map = {}
        for system in root.findall('system'):
            name_elem = system.find('name')
            if name_elem is not None and name_elem.text.strip():
                system_map[name_elem.text.strip()] = system

        # 读取 ext_desc.txt 文件
        with open(ext_desc_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue

                # 分割 system_name 和 extension
                if ',' not in line:
                    print(f"[WARNING] 第 {line_num} 行格式错误：{line}")
                    continue
                parts = line.split(',', 1)
                if len(parts) < 2:
                    print(f"[WARNING] 第 {line_num} 行格式错误：{line}")
                    continue

                system_name = parts[0].strip()
                raw_ext = parts[1].strip()
                # 去除双引号
                if raw_ext.startswith('"') and raw_ext.endswith('"'):
                    extension = raw_ext[1:-1].strip()
                else:
                    extension = raw_ext.strip()

                # 查找 system 节点
                if system_name not in system_map:
                    print(f"[ERROR] 第 {line_num} 行：未找到系统 {system_name}，退出。")
                    sys.exit(1)
                target_system = system_map[system_name]

                # 查找 extension 节点
                ext_elem = target_system.find('extension')
                if ext_elem is None:
                    print(f"[ERROR] 第 {line_num} 行：系统 {system_name} 中未找到 <extension>，退出。")
                    sys.exit(1)
                ext_elem.text = extension

    except IOError as e:
        print(f"[ERROR] 无法读取 {ext_desc_path}：{e}")
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
        print("用法：update_ext.py ext_desc.txt es_systems.cfg")
        sys.exit(1)
    ext_desc_path = sys.argv[1]
    xml_path = sys.argv[2]
    main(ext_desc_path, xml_path)