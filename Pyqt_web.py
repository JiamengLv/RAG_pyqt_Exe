import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QApplication,QMainWindow
from PyQt5.QtCore import Qt
from Answer_question import find_text  
import json
from openai import OpenAI

import json
from openai import OpenAI


client = OpenAI(
        api_key="##########",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


def answer_question(query):
    
    docs = find_text(query)
    
    messages = [
                {
                "role": "assistant",
                "content": "你是一个名叫“智东宝”AI小精灵，负责回答学生和家长的各种问题。",
                },
                {
                "role": "user",
                "content": f"""你是一个名叫“智东宝”AI小精灵，请根据提供的参考资料学生和家长的问题。请按照以下步骤操作：
                    
                    步骤：
                    1. **理解问题**：仔细阅读提出的问题，对用户输入的内容进行识别和判断，如果内容涉及政治、时事、社会问题以及违背道德和法律法规的情形，一律输出:"无法回答该问题，超出我应当回答的范围。“
                    2. **查找相关资料**：在提供的参考资料中，找出与问题高度相关的部分。如果有多段相关内容，请将它们整理在一起。
                    3. **整理信息**：根据找到的相关资料，整理出逻辑清晰的回答。去除重复的内容，并确保信息准确无误。
                    4. **组织回答**：以温和友好的语气组织回答，先介绍自己的身份，然后回答问题。确保回答通俗易懂，适合所有年龄段。
                    5. **处理未找到相关信息的情况**：如果没有找到与问题相关的参考资料，请回答：“对不起，我无法找到与您的问题相关的参考资料。”
                    
                    **参考资料**：
                    {docs}
                    
                    **问题**：
                    {query}
                """
                },
        ]  

    return messages
            

class QnAWidget(QMainWindow):
    def __init__(self):
        
        super().__init__()

        self.setWindowTitle('智东宝”AI小精灵')
        self.setGeometry(100, 100, 800, 500) 
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.setStyleSheet("""
            QnAWidget {
                background-image: url("./background.png");
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;
            }
        """)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)  
        self.layout.setAlignment(Qt.AlignCenter) 


        self.title_label = QLabel("欢迎来咨询“智东宝”AI小精灵", self)
        self.title_label.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #ffffff; 
            background-color: rgba(0, 0, 0, 100);
            padding: 10px; 
            border-radius: 5px;
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)



        self.input_frame = QFrame(self)
        self.input_frame.setStyleSheet("""
            background-color: rgba(255, 255, 255, 230); 
            border-radius: 10px;
            padding: 15px;
        """)
        self.input_layout = QHBoxLayout() 

 
        self.questionInput = QLineEdit(self)
        self.questionInput.setPlaceholderText("在这里输入问题...")
        self.questionInput.setStyleSheet("""
            height: 40px;
            font-size: 16px;
            color: blue; 
            padding: 5px;
            border: 2px solid #ccc;
            border-radius: 5px;
            flex-grow: 1;
        """)
        self.input_layout.addWidget(self.questionInput)

        self.submitButton = QPushButton('提交', self)
        self.submitButton.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """)
        self.submitButton.clicked.connect(self.on_submit)
        self.input_layout.addWidget(self.submitButton)

   
        self.input_frame.setLayout(self.input_layout)
        self.layout.addWidget(self.input_frame)

        self.outputLabel = QLabel("", self)
        self.outputLabel.setStyleSheet("""
            font-size: 16px;
            color: #333;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 12px;
            background-color: rgba(255, 255, 255, 230);
        """)
        self.outputLabel.setWordWrap(True) 
        self.outputLabel.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.addWidget(self.outputLabel)
        

        central_widget.setLayout(self.layout)


        self.setLayout(self.layout)

    def on_submit(self):
        
        question = self.questionInput.text()

        messages = answer_question(question)
        completion = client.chat.completions.create(
            model="qwen1.5-110b-chat",
            messages=messages,
            stream=True,
            stream_options={"include_usage": True}
        )

        response = ""
        for chunk in completion:
            try:
                chunk_data = json.loads(chunk.model_dump_json())
                choices = chunk_data.get("choices", [])

                if len(choices) > 0 and "delta" in choices[0]:
                    delta_content = choices[0]["delta"].get("content", "")
                    if delta_content:
                        response += delta_content

                        self.outputLabel.setText(response)
                        QApplication.processEvents()

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = QnAWidget()
    widget.show()
    sys.exit(app.exec_())