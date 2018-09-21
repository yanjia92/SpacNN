# SpacNN 
A unspecified Markov model checker implemented in Python using neural networks.

## Features
* Suitable for both discrete-time Markov Chain and continuous-time Markov Chain
* Implement multiple function approximation methods to predict final results to give best approximations
* High accuracy comed with pretty fast speed


## Installation
	cd PROJ_ROOT
	sudo pip install -r requirements.txt
	sudo pyinstaller --clean PATH_2_MainUI.py
**If warning no permission, try to add sudo**


## Quick Start
Fellow help documentation after executing the MainUI.exe  
Here is a simple How-to:  
1. executing MainUI.exe by double-click it  
2. open a model file(a .prism file) and edit it. ([syntax](http://prismmodelchecker.org/manual/ThePRISMLanguage/Main "the prism language"))  
3. input a LTL formula. ([syntax](https://en.wikipedia.org/wiki/Linear_temporal_logic))  
4. start training and predictation.  

## File Hierarchy
<pre>
	|--- README.md
	|--- prism_model // prism模型文件
	|--- requirements.txt
	|--- src
	|    |--- checker  // 验证器模块
	|    |--- compiler // 编译模块
	|    |--- config // 配置模块
	|    |--- constant // 常量模块
	|    |--- experiment // 训练模块
	|    |--- model // 模型模块
	|    |--- module // 模块模块
	|    |--- nn // 神经网络模块
	|    |--- scripts // 脚本模块
	|    |--- simulator // 模拟器模块
	|    |--- director // 导演模块
	|    |--- manager // 管理员模块
	|    |--- test // 测试模块
	|    |--- ui // UI模块
	|    |--- util // 辅助模块
<pre>
## Contact
Email: <tonyyj9701@163.com>




