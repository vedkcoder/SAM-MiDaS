import streamlit as st
from streamlit import session_state

import poc_backend as pcb
from st_clickable_images import clickable_images
import io

if 'final_images' not in st.session_state or st.session_state.final_images is None:
    st.session_state.final_images = []
if 'clicked_index' not in st.session_state:
    st.session_state.clicked_index = -1
if 'file_uploader_key' not in st.session_state:
    st.session_state.file_uploader_key = 0
if 'catalogue_key' not in st.session_state:
    st.session_state.catalogue_key = 0
if 'image_sources' not in st.session_state:
    st.session_state.image_sources = []  # Track where each image came from

st.markdown("""
<style>
    /* Hide auto-generated JSON/list output from clickable_images */
    .stMarkdown pre {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)


def delete_final_images():
    st.session_state.final_images = []
    st.session_state.image_sources = []
    st.session_state.clicked_index = -1

    st.session_state.file_uploader_key += 1
    st.session_state.catalogue_key += 1


def remove_image(idx):

    if idx < len(st.session_state.final_images):

        is_catalogue_image = idx < len(st.session_state.image_sources) and st.session_state.image_sources[
            idx] == 'catalogue'

        st.session_state.final_images.pop(idx)
        if idx < len(st.session_state.image_sources):
            st.session_state.image_sources.pop(idx)

        if is_catalogue_image:
            st.session_state.catalogue_key += 1


def image_to_bytes(image_obj):
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG', quality=95)
    img_bytes = img_byte_arr.getvalue()
    return img_bytes


def decode_image(base64_encoded_image):
    return pcb.load_image_from_base64(base64_encoded_image)


def generate_image(user_message, images):
    if images and (user_message and len(user_message.strip()) > 0):
        with st.spinner("Cooking up the image .. ", show_time=True):
            client = pcb.load_client()
            structured_prompt, perspective = pcb.generate_clear_prompt(client=client, user_input=user_message)
            st.text(structured_prompt + '\n' + 'Perspective Requested: ' + str(perspective))

            image_obj_list = pcb.create_image_obj_list(images)

            if len(image_obj_list) > 1:
                response = pcb.generate_response_multiple(client=client, prompt=structured_prompt,
                                                          image_list=image_obj_list)
            elif len(image_obj_list) == 1:
                response = pcb.generate_response_single(client=client, prompt=structured_prompt,
                                                        image=image_obj_list[0])

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
                               mime='image/jpeg')

    elif not user_message or len(user_message.strip()) == 0:
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
                                            key=f"backyards_{st.session_state.catalogue_key}")

        if backyard_clicked >= 0:
            # st.markdown(f"Image #{backyard_clicked} clicked")
            selected_image = backyards[backyard_clicked]
            selected_image = decode_image(selected_image)
            if selected_image not in st.session_state.final_images:
                st.session_state.final_images.append(selected_image)
                st.session_state.image_sources.append('catalogue')
                st.session_state.clicked_index = backyard_clicked
        else:
            print("No image clicked")

    with st.expander('Chairs', expanded=True):
        chairs = catalogue['chairs']
        chair_clicked = clickable_images(chairs,
                                         div_style={"display": "flex",
                                                    "justify-content": "center",
                                                    "flex-wrap": "wrap"},
                                         img_style={"margin": "5px", "height": "200px"},
                                         key=f"chairs_{st.session_state.catalogue_key}")

        if chair_clicked >= 0:
            # st.markdown(f"Image #{chair_clicked} clicked")
            selected_image = chairs[chair_clicked]
            selected_image = decode_image(selected_image)
            if selected_image not in st.session_state.final_images:
                st.session_state.final_images.append(selected_image)
                st.session_state.image_sources.append('catalogue')
                st.session_state.clicked_index = chair_clicked
        else:
            print("No image clicked")

    with st.expander('Tables', expanded=True):
        tables = catalogue['tables']
        tables_clicked = clickable_images(tables,
                                          div_style={"display": "flex",
                                                     "justify-content": "center",
                                                     "flex-wrap": "wrap"},
                                          img_style={"margin": "5px", "height": "200px"},
                                          key=f"tables_{st.session_state.catalogue_key}")

        if tables_clicked >= 0:
            # st.markdown(f"Image #{tables_clicked} clicked")
            selected_image = tables[tables_clicked]
            selected_image = decode_image(selected_image)
            if selected_image not in st.session_state.final_images:
                st.session_state.final_images.append(selected_image)
                st.session_state.image_sources.append('catalogue')
                st.session_state.clicked_index = tables_clicked
        else:
            print("No image clicked")

with st.container(border=True):
    user_message = st.text_input("What do you want to generate today?")

    images = st.file_uploader("Upload an image of your backyard",
                              accept_multiple_files=True,
                              type=["jpg", "jpeg", "png"],
                              key=f"file_uploader_{st.session_state.file_uploader_key}")

    if images:
        for image in images:
            if image not in st.session_state.final_images:
                st.session_state.final_images.append(image)
                st.session_state.image_sources.append('uploaded')

    if len(st.session_state.final_images) > 0:
        st.button("Generate", on_click=generate_image, args=(user_message, st.session_state.final_images))
    else:
        st.warning("Please upload an image")

    if len(st.session_state.final_images) > 0:
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center; color: white;'>Selected Images</h3>", unsafe_allow_html=True)

            for idx, image in enumerate(st.session_state.final_images):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.image(image, width=100)
                with col2:
                    if st.button("❌", key=f"remove_{idx}"):
                        remove_image(idx)
                        st.rerun()

            st.button('Clear All Images', type='primary', on_click=delete_final_images, use_container_width=True)