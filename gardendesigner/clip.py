import argparse
from datetime import datetime
from gardendesigner.config.param import (
    EnvFiler,
    GetEnvParam)
def main():
    """
    命令行逻辑

    Args:
        None
    Returns:
        None

    Example:
        >>> gardendesigner -k mykeys -m gpt-4 -b http://...
        >>> gardendesigner -t "A wonderful scape..."
        >>> gardendesigner -t "..." -e
    """
    parser = argparse.ArgumentParser(
        prog="gardendesigner",
        description="Garden Designer 命令行工具"
    )

    # 配置环境变量 实现一次配置
    parser.add_argument("-k", "--key", help="API Key / 部署密钥")
    parser.add_argument("-m", "--model", help="模型名称")
    parser.add_argument("-b", "--base_url", help="模型接口地址")

    # 配置完毕后 运行核心逻辑传入参数
    parser.add_argument(
        "--text",
        "-t",
        type=str,
        default="A wonderful scape with mountains, water and forests, with almost no artificial traces.",
    )
    parser.add_argument(
        "--edit",
        "-e", 
        action="store_true"
    )
    parser.add_argument(
        "--gen_edit_garden",
        "-g", 
        action="store_true"
    )
    parser.add_argument(
        "--regenerate_infrastructure",
        "-i", 
        action="store_true"
    )
    parser.add_argument(
        "--regenerate_attributes",
        "-a", 
        action="store_true"
    )
    parser.add_argument(
        "--use_conlan",
        "-u", 
        action="store_true"
    )
    parser.add_argument(
        "--use_conlan_layout",
        "-l", 
        action="store_true"
    )

    parser.add_argument("--query", "-q", action="store_true")
    parser.add_argument("--seed", "-s", type=int, default=int(datetime.now().timestamp()))
    parser.add_argument("--checkpoint", "-c", type=str, default="0")
    parser.add_argument("--num", "-n", type=int, default=1)
    args = parser.parse_args()


    is_run = (
        (args.text != parser.get_default("text")) 
        or args.edit 
        or args.gen_edit_garden
        or args.regenerate_infrastructure 
        or args.regenerate_attributes 
        or args.use_conlan 
        or args.use_conlan_layout 
        or args.query 
        or (args.seed != parser.get_default("seed"))
        or (args.checkpoint != parser.get_default("checkpoint"))
        or (args.num != parser.get_default("num"))
    )

    if args.key and is_run:
        parser.error("Error: Config arguments (-k/-m/-b) cannot be used with run arguments.")
    builder = EnvFiler()
    config_path = builder.get_config_path()
    if args.key:
        builder.make(key=args.key,model=args.model,base_url=args.base_url)
    geter = GetEnvParam(config_path=config_path)
    # TODO 核心功能逻辑