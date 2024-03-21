import gradio as gr
import os
import time
from ner_model import get_ehr_details, get_reschedule_details  ,schedule_earliest_appointement, reschedule_earliest_appointement, process_audio


# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.
print("hello")

uploaded_file = False
ehr_data = {}
mp3_uploaded_file = False
mp3_text = ""

def print_like_dislike(x: gr.LikeData):
    print(x.index, x.value, x.liked)


def add_text(history, text):
    history = history + [(text, None)]
    return history, gr.Textbox(value="", interactive=False)


def add_file(history, file):
    global uploaded_file
    global mp3_text
    global mp3_uploaded_file
    file_type = os.path.splitext(file.name)[1]
    print("file type", file_type)
    
    if(file_type == '.txt'):
       with open(file, mode='r', encoding='utf-8-sig') as f:
            text = f.read()
            history = history + [(text, None)]
            uploaded_file = True
            return history
        
    elif(file_type == '.mp3'):
        print("file data", file)
        mp3_text = process_audio([file])
            #print("Transcribed text:", process_audio(audio_bytes))
        mp3_uploaded_file = True
            
             
        
        history = history + [((file.name,), None)]
        return history
                    
    history = history + [((file.name,), None)]
    return history

# def response_genertor(history, response):
#     for word in response.split():
#         history[-1][1] += word + " "
#         time.sleep(0.05)
#         yield history

def bot(history):
    #response = "**That's cool!**"
    global uploaded_file
    global ehr_data
    global mp3_text
    global mp3_uploaded_file
    response=""
    print(type(history[-1][1]))
    history[-1][1] = ""
    if(uploaded_file):
        
        # response = '''Hello {}, From the uploaded document, Doctor recommended following tests {} , {}. 
        # \n Give me few minutes to schedule your appointment \n
        # '''.format('1', '2', '3')
        # for word in response.split():
        #     history[-1][1] += word + " "
        #     time.sleep(0.05)
        #     yield history
         
        ehr_data = get_ehr_details(history[-1][0])
        if 'test' and ('date' or 'time') in ehr_data:
            date = ehr_data['date']['text']
            if 'date' and 'time' in ehr_data:
                date += ehr_data['time']['text']
            response = "Hello {}, From the uploaded document, Doctor recommended following tests {} , {}. \n Give me few minutes to schedule your appointment. \n".format(ehr_data['person']['text'], ehr_data['test']['text'], date)
            for word in response.split():
                history[-1][1] += word + " "
                time.sleep(0.05)
                yield history
            
            response = schedule_earliest_appointement(ehr_data)
            
            time.sleep(2)
            
            for word in response.split():
                history[-1][1] += word + " "
                time.sleep(0.05)
                yield history
                
            uploaded_file = False
        else:
            response = "No tests mentioned to shcedule an appointment. \n"
            for word in response.split():
                history[-1][1] += word + " "
                time.sleep(0.05)
                yield history    
    else:
        if mp3_uploaded_file:
            text = mp3_text[0]['text']
            mp3_uploaded_file = False
        else:
            text =  history[-1][0]
            
        if(len(ehr_data) == 0 ):
             response = "Please upload EHR to fetch the details for scheduling appointment."
             for word in response.split():
                history[-1][1] += word + " "
                time.sleep(0.05)
                yield history
            
        elif(('reschedule' or 'book' or 'appointment' in text)):  
            response = "Let me pull up the slots to reschedule it."
            for word in response.split():
                history[-1][1] += word + " "
                time.sleep(0.05)
                yield history
                
            reschedule_data = get_reschedule_details(text)
            if 'date' in reschedule_data:
                response = reschedule_earliest_appointement(ehr_data, (reschedule_data['date']['text']))
            else:
                response = "Please include which month and day you want to reschedule your appointment."
            
            time.sleep(2)
            
            for word in response.split():
                history[-1][1] += word + " "
                time.sleep(0.05)
                yield history
                
            
        
            # response = reschedule_appointment(reschedule_data['date']['text'], ehr_data['patient_id']['text'])
            
            
def greet(name):
    return "Hello " + name + "!"
            
examples=[ "Can you reschedule my appointment to <Date>."]            

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        [],
        value = "Please upload your EHR to schedule an appointment",
        elem_id="chatbot",
        height = '80vh',
        bubble_full_width=False,
        # avatar_images=(None, (os.path.join(os.path.dirname(__file__), "avatar.png"))),
    )

    with gr.Column():
        with gr.Row():
            txt = gr.Textbox(
                scale=10,
                show_label=False,
                placeholder="Enter the query and press enter or upload a EHR file or drop a voice message",
                container=False,
            )
                #inter = gr.Interface(greet, inputs=txt,  outputs=None, submit_btn=False,  examples=examples)
            
            
            btn = gr.UploadButton("📁", file_types=["image", "video", "audio", "text"],  scale = 1)
            clear = gr.ClearButton([txt, chatbot]) 
        
        gr.Examples(examples=examples, inputs = txt, fn = greet, outputs=None)

    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
        bot, chatbot, chatbot, api_name="bot_response"
    )
    txt_msg.then(lambda: gr.Textbox(interactive=True), None, [txt], queue=False)
    
    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
        bot, chatbot, chatbot
    )

    # chatbot.like(print_like_dislike, None, None)


demo.queue()
demo.launch()


# import gradio as gr
# import os
# import time
# from ner_model import get_ehr_details, get_reschedule_details  ,schedule_earliest_appointement, reschedule_appointment, reschedule_earliest_appointement


# def get_answer_local(query, history):
#     pass

# def get_answer_global(query, history):
#     pass



# with gr.Blocks(theme=gr.themes.Default(text_size=gr.themes.sizes.text_lg)) as demo:
#     with gr.Row(equal_height=True):
#         with gr.Column(scale=2):                             
#             with gr.Tab("Scheduler"):
#                 chatbot_global = gr.ChatInterface(
#                     get_answer_global,
#                     examples=[
#                         ["How many patients were prescribed <this drug>?"],
#                         ["How many patients with <disease> were prescribed <this drug>?"],
#                         ["In how many cases did <this drug> cause adverse reactions?"],
#                         ["How many patients with <disease> underwent <test>?"]
#                     ],
#                     css=''
#                 )
#     # text_button.click(text_analysis, inputs=text_input, outputs=[text_output,text_table_output,text_graph,text_graph_full])
#     # upload_button.upload(upload_file, upload_button, outputs=[upload_output,upload_table_output,upload_graph,upload_graph_full])
#     # show_graph_button.click(draw_subgraphs, outputs=[upload_subgraphs, upload_bridgedgraphs])

# demo.launch()