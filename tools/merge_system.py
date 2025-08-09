import sys
import xml.etree.ElementTree as ET

def main(extra_path, target_path):
    try:
        # 解析目标 XML 文件
        target_tree = ET.parse(target_path)
        target_root = target_tree.getroot()
    except ET.ParseError as e:
        print(f"[ERROR] 目标 XML 解析失败：{e}")
        sys.exit(1)
    except IOError as e:
        print(f"[ERROR] 无法打开目标 XML 文件 {target_path}：{e}")
        sys.exit(1)

    try:
        # 解析 extra XML 文件
        extra_tree = ET.parse(extra_path)
        extra_root = extra_tree.getroot()
    except ET.ParseError as e:
        print(f"[ERROR] 额外 XML 解析失败：{e}")
        sys.exit(1)
    except IOError as e:
        print(f"[ERROR] 无法打开额外 XML 文件 {extra_path}：{e}")
        sys.exit(1)

    # 找出所有的 <system> 元素
    extra_systems = extra_root.findall('system')
    if not extra_systems:
        print("[WARNING] 额外 XML 中没有找到任何 <system> 元素。")
        sys.exit(0)

    # 逐个添加到目标 XML 中
    for system in extra_systems:
        # 复制整个 <system> 元素
        new_system = ET.fromstring(ET.tostring(system, encoding='utf-8'))

        # 设置换行和缩进
        new_system.tail = '\n'  # 每个 <system> 之间换行
        for child in new_system:
            child.tail = '\n\t'  # 子节点缩进
        if new_system[-1] is not None:
            new_system[-1].tail = '\n'  # 最后一个子节点换行

        # 添加到目标 XML 的根元素末尾
        target_root.append(new_system)

    try:
        # 写回目标 XML 文件
        target_tree.write(target_path, encoding='UTF-8', xml_declaration=True)
        print("[INFO] XML 文件已更新。")
    except IOError as e:
        print(f"[ERROR] 写入 XML 文件失败：{e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法：merge_extra_system.py extra_system.cfg es_systems.cfg")
        sys.exit(1)
    extra_path = sys.argv[1]
    target_path = sys.argv[2]
    main(extra_path, target_path)