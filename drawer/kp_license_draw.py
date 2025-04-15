from PIL import Image, ImageDraw, ImageFont
import requests
import os

from utils.log import Logos


class CertificateGenerator:
    def __init__(self, log:Logos,kp_background_path:str,pl_background_path:str,ob_background_path:str,dice_background_path:str, output_folder:str, default_avatar_path:str, chinese_font_path:str = "resource/fonts/FangSong.ttf", english_font_path:str = "resource/fonts/Times New Roman.ttf" ):
        self.kp_background_path = kp_background_path
        self.pl_background_path = pl_background_path
        self.ob_background_path = ob_background_path
        self.dice_background_path = dice_background_path
        self.chinese_font_path = chinese_font_path
        self.english_font_path = english_font_path
        self.output_folder = output_folder
        self.log = log
        self.default_avatar_path = default_avatar_path
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    @staticmethod
    def download_image(url, save_path):
        try:
            print(f"下载图片: {url}")
            # 检查保存路径所在的目录是否存在，若不存在则创建
            save_dir = os.path.dirname(save_path)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # 发送 HTTP 请求获取图片内容
            response = requests.get(url, stream=True, timeout=(3.05, 10))
            response.raise_for_status()

            # 保存图片到本地
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

            return save_path

        except requests.RequestException as e:
            print(f"下载图片失败（网络请求异常）: {e}")
        except FileNotFoundError as e:
            print(f"下载图片失败（文件操作异常）: {e}")
        except Exception as e:
            print(f"下载图片失败（未知异常）: {e}")

        return None

    @staticmethod
    def _draw_bold_text(draw, position, text, font, fill=(0, 0, 0), bold_level=2):
        """绘制加粗文字
        Args:
            draw: ImageDraw对象
            position: (x, y) 文字位置
            text: 要绘制的文字
            font: 字体对象
            fill: 颜色
            bold_level: 加粗级别(1-3)
        """
        x, y = position
        for offset in range(1, bold_level+1):
            draw.text((x+offset, y+offset), text, fill=fill, font=font)
        draw.text((x, y), text, fill=fill, font=font)

    @staticmethod
    def _draw_centered_text(draw, x_range, y_pos, text, font, fill=(0, 0, 0),
                            bold=False):
        """绘制居中对齐文字
        Args:
            x_range: (left, right) 左右边界坐标
            bold: 是否加粗
        Raises:
            ValueError: 当文本过长且字体小于24时抛出
        """
        while True:
            text_width = draw.textlength(text, font=font)
            left, right = x_range
            x_pos = left + (right - left - text_width) // 2
            if text_width <= right - left:
                break
            # 缩小字体大小
            font_size = font.size - 1
            if font_size < 24:  # 添加最小字体检查
                raise ValueError(f"文本过长无法适应区域: '{text}' (最小字体24px)")
            font = ImageFont.truetype(font.path, font_size)
            y_pos = y_pos + 1


        if bold:
            for offset in range(1, 3):
                draw.text((x_pos + offset, y_pos + offset), text, fill=fill, font=font)
        draw.text((x_pos, y_pos), text, fill=fill, font=font)

    @staticmethod
    def _draw_text(draw, position, text, font, fill=(0, 0, 0), bold=False):
        x, y = position
        draw.text((x, y), text, fill=fill, font=font)

    def generate_certificate(self, certificate_id,role, name, avatar_url, date,level):
        output_path = os.path.join(self.output_folder, f"certificate_{certificate_id}.jpg")
        level = int(level)
        match level:
            case 1:
                level = "初级"
            case 2:
                level = "中级"
            case 3:
                level = "高级"
            case _:
                level = "初级"
        match role:
            case "kp":
                background_path = self.kp_background_path
            case "pl":
                background_path = self.pl_background_path
            case "ob":
                background_path = self.ob_background_path
            case "dice":
                background_path = self.dice_background_path
            case _:
                background_path = self.kp_background_path
        # 打开背景图片并转换为RGB模式
        background = Image.open(background_path).convert('RGB')
        draw = ImageDraw.Draw(background)

        avatar_path = f"data/temp/avatar_{certificate_id}.jpg"
        try:
            # 尝试下载头像
            downloaded_avatar = self.download_image(avatar_url, avatar_path)
            if downloaded_avatar:
                try:
                    # 尝试打开下载的头像并转换为RGB模式
                    avatar = Image.open(downloaded_avatar).convert('RGB')
                except Exception as e:
                    self.log.error(f"加载头像（{avatar_url}）失败: {e}; 使用默认头像")
                    avatar = Image.open(self.default_avatar_path).convert('RGB')
            else:
                # 下载失败使用默认头像
                avatar = Image.open(self.default_avatar_path).convert('RGB')
        except Exception as e:
            self.log.error(f"下载头像({avatar_url})失败: {e}; 使用默认头像")
            avatar = Image.open(self.default_avatar_path).convert('RGB')

        # 调整头像大小并粘贴到背景上
        avatar = avatar.resize((386, 386))
        background.paste(avatar, (1341, 487))

        # 修改字体设置
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            script_dir= os.path.dirname(script_dir)
            font_path_l = os.path.join(script_dir, self.chinese_font_path)
            font_path_m = os.path.join(script_dir, self.english_font_path)
            font_l = ImageFont.truetype(font_path_l, size=48)
            font_m = ImageFont.truetype(font_path_m, size=36)
        except Exception as e:
            self.log.error(f"绘制证书{certificate_id}时加载字体失败: {e}; 使用默认字体")
            font_l = ImageFont.load_default(size=48)
            font_m = ImageFont.load_default(size=36)
        try:
            self._draw_text(draw, (825, 463), f"{certificate_id}", font_m)
            self._draw_centered_text(draw, (415, 720), 674, f"{name}", font_l, fill=(0, 0, 0), bold=True)
            if role !="dice":
                self._draw_centered_text(draw, (370, 580), 817, f"{level}", font_l, fill=(0, 0, 0), bold=True)
            self._draw_bold_text(draw, (1300, 975), f"{date}", font_l)
        except Exception as e:
            raise e

        # 保存为JPEG格式
        background.save(output_path, format='JPEG', quality=95)

        # 清理临时头像文件
        if os.path.exists(avatar_path):
            os.remove(avatar_path)

    def batch_generate_certificates(self, data_list):
        for index, data in enumerate(data_list):
            certificate_id = data.get('certificate_id')
            name = data.get('name')
            avatar_url = data.get('avatar_url')
            date = data.get('date')
            level = data.get('level')
            role = data.get('role')
            output_path = os.path.join(self.output_folder, f"certificate_{certificate_id}.jpg")
            try:
                self.generate_certificate(certificate_id, name, role,avatar_url, date, level)
            except Exception as e:
                self.log.error(f"生成证书{certificate_id}失败: {e}")
