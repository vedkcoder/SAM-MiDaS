import streamlit as st
import poc_backend as pcb
from st_clickable_images import clickable_images
import io

if 'final_images' not in st.session_state:
    st.session_state.final_images = []
if 'clicked_index' not in st.session_state:
    st.session_state.clicked_index = -1

selected_images = []

st.markdown("""
<style>
    /* Hide auto-generated JSON/list output from clickable_images */
    .stMarkdown pre {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

def image_to_bytes(image_obj):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG', quality=95)
    img_bytes = img_byte_arr.getvalue()

    return img_bytes

def decode_image(base64_encoded_image):
    return pcb.load_image_from_base64(base64_encoded_image)

def generate_image(user_message, images):
    if images and user_message:

        with st.spinner("Cooking up the image .. ", show_time=True):
            client = pcb.load_client()
            structured_prompt, perspective = pcb.generate_clear_prompt(client=client, user_input=user_message)
            st.text(structured_prompt + '\n' + 'Perspective Requested: ' + str(perspective))

            image_obj_list = pcb.create_image_obj_list(images)

            if len(image_obj_list) > 1:
                response = pcb.generate_response_multiple(client=client, prompt=structured_prompt,
                                                      image_list=image_obj_list)
            elif len(image_obj_list) == 1:
                response = pcb.generate_response_single(client=client, prompt=structured_prompt, image=image_obj_list[0])

            output = pcb.extract_output(response)

            if perspective:
                if perspective.lower() not in ['none', 'null', 'empty']:
                    perspective_image = pcb.load_image(output['image'])

                    perspective_prompt = structured_prompt + f'Make sure to use the following perspective {perspective}'
                    response = pcb.generate_perspective(client, perspective_image, perspective_prompt)
                    output = pcb.extract_output(response)

            try:
                st.text(output['text'])
            except Exception as e:
                print('No text generated', e)

            st.image(output['image'])
            st.download_button('Save Image',
                               data=image_to_bytes(output['image']),
                               file_name='image.jpg',
                               icon=':material/download:',
                               mime='image/jpeg',
                               on_click='ignore')

    elif not user_message:
        st.warning("Please enter your message.")
    elif not images:
        st.warning("Please upload an image.")


with st.sidebar:
    st.title('Catalogue')
    catalogue = pcb.load_catalogue()

    with st.expander('Sample Backyards', expanded=True):
        backyards = catalogue['backgrounds']
        backyard_clicked = clickable_images(backyards,
                                           div_style={"display": "flex",
                                                     "justify-content": "center",
                                                     "flex-wrap": "wrap"},
                                           img_style={"margin": "5px", "height": "200px"},
                                           key="backyards")

        if backyard_clicked >= 0:
            st.markdown(f"Image #{backyard_clicked} clicked")
            selected_image = backyards[backyard_clicked]
            if selected_image not in st.session_state.final_images:
                selected_image = decode_image(selected_image)
                selected_images.append(selected_image)
                st.session_state.clicked_index = backyard_clicked
        else:
            st.markdown("No image clicked")

    with st.expander('Chairs', expanded=True):
        chairs = catalogue['chairs']
        chair_clicked = clickable_images(chairs,
                                        div_style={"display": "flex",
                                                  "justify-content": "center",
                                                  "flex-wrap": "wrap"},
                                        img_style={"margin": "5px", "height": "200px"},
                                        key="chairs")

        if chair_clicked >= 0:
            st.markdown(f"Image #{chair_clicked} clicked")
            selected_image = chairs[chair_clicked]
            if selected_image not in st.session_state.final_images:
                selected_image = decode_image(selected_image)
                selected_images.append(selected_image)
                st.session_state.clicked_index = chair_clicked
        else:
            st.markdown("No image clicked")

    with st.expander('Tables', expanded=True):
        tables = catalogue['tables']
        tables_clicked = clickable_images(tables,
                                         div_style={"display": "flex",
                                                   "justify-content": "center",
                                                   "flex-wrap": "wrap"},
                                         img_style={"margin": "5px", "height": "200px"},
                                         key="tables")

        if tables_clicked >= 0:
            st.markdown(f"Image #{tables_clicked} clicked")
            selected_image = tables[tables_clicked]
            if selected_image not in st.session_state.final_images:
                selected_image = decode_image(selected_image)
                selected_images.append(selected_image)
                st.session_state.clicked_index = tables_clicked
        else:
            st.markdown("No image clicked")


with st.container(border=True):
    user_message = st.text_input("What do you want to generate today?")
    images = st.file_uploader("Upload an image of your backyard",
                              accept_multiple_files=True,
                              type=["jpg", "jpeg", "png"])

    for image in images:
        if image not in st.session_state.final_images:
            selected_images += [image]

    if len(selected_images) > 0:
        st.button("Generate", on_click=generate_image, args=(user_message, selected_images))
    else:
        st.warning("Please upload an image")

    if len(selected_images) > 0:
        with st.container(border=True):
            st.title('Selected Images')
            for image in selected_images:
                st.image(image, width=50)