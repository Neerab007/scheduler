import gradio as gr
import os
import time
from ner_model import get_ehr_details, get_reschedule_details  ,schedule_earliest_appointement, reschedule_appointment, reschedule_earliest_appointement



# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.


uploaded_file = False
ehr_data = {}

def print_like_dislike(x: gr.LikeData):
    print(x.index, x.value, x.liked)


def add_text(history, text):
    history = history + [(text, None)]
    return history, gr.Textbox(value="", interactive=False)


def add_file(history, file):
    global uploaded_file
    file_type = os.path.splitext(file.name)[1]
    
    if(file_type == '.txt'):
       with open(file, mode='r', encoding='utf-8-sig') as f:
            text = f.read()
            history = history + [(text, None)]
            uploaded_file = True
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
            
            time.sleep(1)
            
            for word in response.split():
                history[-1][1] += word + " "
                time.sleep(0.05)
                yield history
                
            uploaded_file = False
    else:
        if(len(ehr_data) == 0 ):
             response = "Please upload your EHR to fetch your details."
             for word in response.split():
                history[-1][1] += word + " "
                time.sleep(0.05)
                yield history
            
        elif(('reschedule' or 'book' or 'appointment' in history[-1][0])):  
            response = "Let me pull up the slots to reschedule it."
            for word in response.split():
                history[-1][1] += word + " "
                time.sleep(0.05)
                yield history
                
            reschedule_data = get_reschedule_details(history[-1][0])
            response = reschedule_earliest_appointement(ehr_data, (reschedule_data['date']['text']))
            
            for word in response.split():
                history[-1][1] += word + " "
                time.sleep(0.05)
                yield history
                
            
        
            # response = reschedule_appointment(reschedule_data['date']['text'], ehr_data['patient_id']['text'])
            
            
            
gr.ChatInterface    


with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        [],
        value = "Please upload your EHR to schedule an appointment",
        elem_id="chatbot",
        height = '80vh',
        bubble_full_width=False,
        # avatar_images=(None, (os.path.join(os.path.dirname(__file__), "avatar.png"))),
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter the query or upload a EHR file",
            container=False,
        )
        btn = gr.UploadButton("📁", file_types=["image", "video", "audio", "text"])

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