import streamlit as st
import pickle
import numpy as np
import time
import os

# Define path to saved artifacts.
parent_dir = os.path.dirname(os.getcwd())
artifact_dir = os.path.join(parent_dir,'artifacts')

# Load precomputed datasets
book_data = pickle.load(open(f'{artifact_dir}/book_data.pkl','rb'))               # Book metadata (title, author, year, etc.)
similarity_data = pickle.load(open(f'{artifact_dir}/similarity_data.pkl','rb'))   # Precomputed similarity matrix between books
popular_books = pickle.load(open(f'{artifact_dir}/top_50_books.pkl','rb'))        # Top 50 popular books data

def get_book_details(book : str) -> np.ndarray:
    """
    Fetch details of the book from book_data.
    
    Args:
        book (str): Title of the book.
    
    Returns:
        np.array: Book details as a numpy array.
    """
    # Fetch matching book row
    book_details = np.array(book_data[book_data['Book-Title']==book])[0]
    return book_details


def recommend_book(book : str) -> list:
    """
    Recommend similar books based on similarity scores.

    Args:
        book (str): Title of the selected book.

    Returns:
        list: List of similar book titles.
    """
    # Sort books based on similarity scores in descending order, skip the first (itself)
    similar_items = sorted(list(enumerate(similarity_data.loc[book])),key=lambda x:x[1],reverse=True)[1:11]
    similar_books = [similarity_data.index[i[0]] for i in similar_items]
    return similar_books

def update_recom()->None:
    """
    Toggle the recommendation visibility state in the session.(show/hide).
    """
    if st.session_state.recom == 0:
          st.session_state.recom = 1
    else:
         st.session_state.recom = 0

def render(selected_book : str )->None :
    """
    Render the selected book details and handle the recommendation toggle.

    Args:
        selected_book (str): Title of the selected book.
    """
    # Fetch book details
    temp = get_book_details(selected_book)
    
    # Display the book details in a container
    with st.container(border=True,):
        _,img,details=st.columns([1,4,4])       # Layout: left padding, image, details
        with img:
            st.title(temp[0])    # Book Title
            st.write('')
            st.image(temp[4],width=250)   # Book Cover Image
            st.title('')
        with details:
            for i in range(2):
                    st.title('')           # Add vertical spacing

             # Display author, year, publisher, and rating   
            st.markdown(f'<b style="font-size:20px;">Author &nbsp;&nbsp;:&nbsp;&nbsp; &nbsp;&nbsp;</b><b style="font-size:30px;">{str(temp[1])}</b>', unsafe_allow_html=True)
            st.markdown(f'<b style="font-size:20px;">Year &nbsp;&nbsp;:&nbsp;&nbsp; &nbsp;&nbsp;</b><b style="font-size:30px;">{str(temp[2])}</b>', unsafe_allow_html=True)
            st.markdown(f'<b style="font-size:20px;">Publisher&nbsp;&nbsp;:&nbsp;&nbsp; &nbsp;&nbsp;</b><b style="font-size:30px;">{temp[3]}</b>', unsafe_allow_html=True)
            st.markdown(f'<b style="font-size:20px;"> Rating &nbsp;&nbsp;:&nbsp;&nbsp; &nbsp;&nbsp;</b><b style="font-size:30px;">{np.round(temp[5],1)}</b>', unsafe_allow_html=True)

    st.title('')
    _,ctntn,_ = st.columns([1,.7,1])        # Center the button horizontally
    with ctntn:
        # Button to show or hide recommendations
        if st.session_state.recom == 0:
            recom_butt = st.button('show recommendation',type="primary",use_container_width=True,on_click=update_recom)
        else:
             recom_butt = st.button('hide recommendation',type="primary",use_container_width=True,on_click=update_recom)
        st.title('')

    # If recommendation state is active, show recommended books   
    if st.session_state.recom == 1:
        get_recommendation(selected_book)
        


def update_session(new_book : str,reset:int = None)->None:
    """
    Update the session state when selecting a book or resetting to home.

    Args:
        new_book (str): Title of the new selected book.
        reset (int, optional): If provided, resets the session to the home page.
    """
    
    st.session_state.book = new_book
    if reset:
          st.session_state.level=0
          st.session_state['booked']=None
    else:
         st.session_state.level=1
         st.session_state.recom=0


def get_recommendation(selected_book:str)->None:
    """
    Render recommended books based on similarity to the selected book.

    Args:
        selected_book (str): Title of the selected book.
    """
    
    similar_books = recommend_book(selected_book)   # Get similar books

    # Display the first 5 recommended books in a horizontal layout
    cols1 = st.columns(5,gap='medium')
    for i,j in enumerate(cols1):
        with j:
            with st.container(border=True,height=450):
                temp = get_book_details(similar_books[i])
                st.image(temp[4],use_container_width=True)
                st.button('view',key=i,on_click=update_session,args=(similar_books[i],))
                st.write(similar_books[i])
                    
    st.header('')

    # Display the next 5 recommended books
    cols2 = st.columns(5)
    for i,j in enumerate(cols2):
        with j:
            with st.container(border=True,height=480):
                temp = get_book_details(similar_books[i+5])
                st.image(temp[4],use_container_width=True)
                st.button('view',key=i+5,on_click=update_session,args=(similar_books[i+5],))
                st.write(similar_books[i+5])
                    
# Configure the Streamlit page
st.set_page_config(layout="wide")

# Initialize session state variables if not present
if 'book' and 'level' and 'recom' not in st.session_state:
    st.session_state.book = 0
    st.session_state.level = 0
    st.session_state.recom = 0

# Create tabs for Explore and Trending
explore,trending = st.tabs(['Explore','Trending'])

# Explore Tab
with explore:
    _,center,_ = st.columns([1,15,1])
    with center:
        title,home = st.columns([8,2])
        with home:
            st.title('')   
            st.button('home',on_click=update_session,args=(0,1))
        with title:
            st.title('Book Recommendation System',anchor=False)  

        # Book selection drop-down
        if st.session_state.level==0:
            selected = center.selectbox('book',book_data['Book-Title'],index=None,placeholder="select a book",label_visibility='hidden',key='booked')
            st.write('')
            if selected :
                st.session_state.book = selected

        # If a book is selected, render the book details
        if st.session_state.book != 0:
            render(st.session_state.book)
                    
# Trending Tab
with trending:
    st.title('Popular Books',anchor=False)    

    # Loop to display the top 50 popular books in 10 rows of 5 columns
    cols = st.columns(5,gap='large')
    for r in range(10):
        for i,j in enumerate(cols):
            with j:
                st.write(' ')
                with st.container(border=True,height=460):  
                    temp=get_book_details(popular_books[i+(r*5),0])
                    st.write('Rating  : ',np.round(popular_books[i+(r*5),1],2))
                    st.image(temp[4],use_container_width=True,)
                    st.write(popular_books[i,0])
                
