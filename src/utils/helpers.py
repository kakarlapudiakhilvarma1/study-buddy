import os
import streamlit as st
import pandas as pd
from src.generator.question_generator import QuestionGenerator


class QuizManager:
    def __init__(self):
        self.questions=[]
        self.user_answers=[]
        self.results=[]
    
    def clear_widget_values(self):
        """Clear all widget values from session state"""
        # Clear ALL quiz-related keys from session state
        keys_to_remove = []
        for key in st.session_state.keys():
            if key.startswith('mcq_') or key.startswith('fill_blank_'):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del st.session_state[key]


    def generate_questions(self,generator:QuestionGenerator,topic:str,question_type:str,difficulty:str,num_questions:int) -> bool:

        self.questions=[]
        self.user_answers=[]
        self.results=[]

        # Clear previous widget values from session state
        self.clear_widget_values()

        try:
            for _ in range(num_questions):
                if question_type=="Multiple Choice":
                    question=generator.generate_mcq(topic,difficulty.lower())

                    self.questions.append({
                        'type' : 'MCQ',
                        'question' : question.question,
                        'options' : question.options,
                        'correct_answer' : question.correct_answer
                    })

                else:
                    question=generator.generate_fill_blank(topic,difficulty.lower())

                    self.questions.append({
                        'type' : 'Fillblanks',
                        'question' : question.question,
                        'correct_answer' : question.answer
                    })
                
        except Exception as e:
            st.error(f"Error generating question {e}")
            return False
        
        return True
    

    def attempt_quiz(self):
        # Clear previous answers when displaying quiz
        self.user_answers = []

        for i,q in enumerate(self.questions):
            st.markdown(f"**Question {i+1} : {q['question']}**")

            if q['type']=='MCQ':
                st.radio(
                    label=f"Select an answer for Question {i+1}",
                    options=q['options'],
                    key=f"mcq_{i}"
                )

            else:
                widget_key = f"fill_blank_{i}"
                if widget_key not in st.session_state:
                    st.session_state[widget_key] = ""
                st.text_input(
                    label=f"Fill in the blank for Question {i+1}",
                    placeholder="Fill in the blank.",
                    key = widget_key,
                    value=""
                )

    def collect_answers(self):
        """Collect answers from session state after user submits"""
        self.user_answers = []
        
        for i, q in enumerate(self.questions):
            if q['type'] == 'MCQ':
                # Get the answer from session state
                answer = st.session_state.get(f"mcq_{i}", "")
                self.user_answers.append(answer)
            else:
                # Get the answer from session state
                answer = st.session_state.get(f"fill_blank_{i}", "")
                self.user_answers.append(answer)


    def evaluate_quiz(self):
        # First collect the answers from session state
        self.collect_answers()

        self.results=[]

        for i, (q,user_ans) in enumerate(zip(self.questions,self.user_answers)):
            result_dict = {
                'question_number' : i+1,
                'question' : q['question'],
                'question_type' : q['type'],
                'user_answer' : user_ans,
                'correct_answer' : q['correct_answer'],
                'is_correct' : False
            }

            if q['type'] == 'MCQ':
                result_dict['options'] = q['options']
                result_dict['is_correct'] = user_ans == q['correct_answer']

            else:
                result_dict['options'] = []
                result_dict['is_correct'] = user_ans.strip().lower() == q['correct_answer'].strip().lower()

            self.results.append(result_dict)


    def generate_result_dataframe(self):
        if not self.results:
            return pd.DataFrame()
        
        return pd.DataFrame(self.results)
    
    def save_to_csv(self,filename_prefix='quiz_results'):
        if not self.results:
            st.warning("No results to save !!")
            return None
        
        df = self.generate_result_dataframe()

        from datetime import datetime
        timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename=f"{filename_prefix}_{timestamp}.csv"

        os.makedirs('results',exist_ok=True)
        full_path=os.path.join('results',unique_filename)

        try:
            df.to_csv(full_path,index=False)
            st.success("Results saved successfully...")
            return full_path
        
        except Exception as e:
            st.error(f"Failed to save results {e}")
            return None