# chaoxing_tool

超星/学习通/尔雅 助手，帮助用户一键完成任务点、下载课程资源等。基于 Python 语言和 requests 包。

本分支是基于原项目的重构，拥有更高的可扩展性和功能的低耦合性，方便更多开发者参与贡献。

项目拥有的Log输出，方便开发者更好的还原用户使用出错时的场景。

## 功能

基础功能如下：

- 用户登录
  - 手机号登录
  - Cookie 登录
- 获取 用户/课程/章节 等数据
- 日志输出
- 程序配置读取与保存

扩展功能如下：

- 一键完成课程中的任务点

  <details>

  ![deal_mission](./static/func_deal_mission.jpg)

  </details>

- 下载课程中的资源

  <details>

  ![media_download](./static/func_media_download.jpg)

  </details>

- 刷取课程学习次数

  <details>

  ![media_download](./static/func_set_log.jpg)

  </details>

- 刷取课程视频观看时长

  <details>

  ![media_download](./static/func_set_time.jpg)

  </details>

## 使用说明

以下有两种使用方式，请根据您个人的实际情况与需求选择

### 可执行文件运行

**如果您此前未接触过Python或其他编程语言，且只想直接快捷的使用本工具，请优先选择本方法。**

**但需要注意本方法的文件只能在Windows上运行，不支持Mac**

1. 打开本项目的 [Release](https://github.com/liuyunfz/chaoxing_tool/releases/latest) 页面
2. 下载其中的`chaoxing_tool.zip`压缩包
3. 选择一个储存位置对压缩包进行解压
4. 找到`main.exe`文件双击运行

### 源文件运行

请确保您的电脑拥有`Python3`环境，以及本项目所需要用的package。

首先下载本项目的代码源文件，您可以使用Github自带的Zip download或者使用Git命令`git clone git@github.com:liuyunfz/graph-project.git`

然后对项目需要的第三方包进行安装，您可以直接用pip进行安装`pip install -r requirements.txt`，亦或是使用诸如`virtualenv`的虚拟环境进行安装。

最后通过`python main.py`运行`mian.py`文件即可

## 已知问题

详见 [本项目的Bug](https://github.com/liuyunfz/chaoxing_tool/labels/bug)

## Contribute

如果您也想参与到本项目的开发中，包括但不限于新功能的添加、文档的优化。

请阅读本项目的规范文档（还没写），Fork之后提交Pr即可。

## 免责声明

本项目遵循 [GPL-3.0 License](https://github.com/liuyunfz/chaoxing_tool/blob/master/LICENSE) ，仅作为学习途径使用，请勿用于商业用途或破坏他人的知识产权

