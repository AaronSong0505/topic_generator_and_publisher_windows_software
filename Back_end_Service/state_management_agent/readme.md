和前端客户端交互以及后端其余agent通信都是通过该模块完成。此外还进行整个后端流程的pipline控制。可以理解为前端和所有后端服务的中间件。
pipline：
- 和llm-agent通信，获得返回结果。将结果解析后展示到前端。
- 将llm-agent返回的结果解析后发送给image-generator-agent，获得返回结果。将结果解析后展示到前端。
- 将llm-agent结果和image-generator-agent结果推动到publisher-agent，获得该agent结果。将结果解析后展示到前端。

记得在该项目本目录下创建requirements.txt文件，记录需要使用的安装依赖。