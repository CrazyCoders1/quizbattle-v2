#!/usr/bin/env python3
"""
Script to populate the database with comprehensive questions for all exam types and difficulties
that match the challenge creation options exactly.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import QuizQuestion

def populate_questions():
    """Populate database with comprehensive questions for all combinations"""
    
    app = create_app()
    
    with app.app_context():
        # Clear existing questions (optional)
        # QuizQuestion.query.delete()
        
        # Comprehensive questions for all exam types and difficulties
        questions_data = [
            # CBSE 11 - Easy Questions
            {
                "text": "What is the SI unit of electric current?",
                "options": ["Volt", "Ampere", "Ohm", "Watt"],
                "answer": 1,
                "difficulty": "easy",
                "exam_type": "CBSE 11"
            },
            {
                "text": "Which gas is most abundant in Earth's atmosphere?",
                "options": ["Oxygen", "Carbon dioxide", "Nitrogen", "Argon"],
                "answer": 2,
                "difficulty": "easy",
                "exam_type": "CBSE 11"
            },
            {
                "text": "What is the chemical formula of water?",
                "options": ["H2O", "CO2", "NaCl", "C6H12O6"],
                "answer": 0,
                "difficulty": "easy",
                "exam_type": "CBSE 11"
            },
            {
                "text": "What is the speed of light in vacuum?",
                "options": ["3 × 10^8 m/s", "3 × 10^6 m/s", "9 × 10^8 m/s", "1 × 10^8 m/s"],
                "answer": 0,
                "difficulty": "easy",
                "exam_type": "CBSE 11"
            },
            {
                "text": "Which planet is known as the Red Planet?",
                "options": ["Venus", "Jupiter", "Mars", "Saturn"],
                "answer": 2,
                "difficulty": "easy",
                "exam_type": "CBSE 11"
            },
            
            # CBSE 11 - Medium Questions
            {
                "text": "A body is moving with uniform velocity. What is its acceleration?",
                "options": ["Zero", "Constant", "Increasing", "Decreasing"],
                "answer": 0,
                "difficulty": "medium",
                "exam_type": "CBSE 11"
            },
            {
                "text": "What type of chemical bond is formed between sodium and chlorine in NaCl?",
                "options": ["Covalent bond", "Metallic bond", "Ionic bond", "Hydrogen bond"],
                "answer": 2,
                "difficulty": "medium",
                "exam_type": "CBSE 11"
            },
            {
                "text": "If sin θ = 3/5, what is cos θ?",
                "options": ["4/5", "3/4", "5/4", "5/3"],
                "answer": 0,
                "difficulty": "medium",
                "exam_type": "CBSE 11"
            },
            
            # CBSE 11 - Tough Questions
            {
                "text": "The work function of a metal is 3.2 eV. What is the maximum kinetic energy of photoelectrons when light of wavelength 300 nm is incident on it?",
                "options": ["0.94 eV", "1.2 eV", "0.75 eV", "2.1 eV"],
                "answer": 0,
                "difficulty": "tough",
                "exam_type": "CBSE 11"
            },
            
            # CBSE 12 - Easy Questions
            {
                "text": "What is the derivative of x²?",
                "options": ["x", "2x", "x²", "2x²"],
                "answer": 1,
                "difficulty": "easy",
                "exam_type": "CBSE 12"
            },
            {
                "text": "Which of the following is a greenhouse gas?",
                "options": ["Nitrogen", "Oxygen", "Carbon dioxide", "Helium"],
                "answer": 2,
                "difficulty": "easy",
                "exam_type": "CBSE 12"
            },
            {
                "text": "What is the unit of electric potential?",
                "options": ["Ampere", "Volt", "Ohm", "Coulomb"],
                "answer": 1,
                "difficulty": "easy",
                "exam_type": "CBSE 12"
            },
            {
                "text": "The integration of 2x is:",
                "options": ["x²", "x² + C", "2x²", "2"],
                "answer": 1,
                "difficulty": "easy",
                "exam_type": "CBSE 12"
            },
            {
                "text": "Which element has atomic number 1?",
                "options": ["Helium", "Hydrogen", "Lithium", "Carbon"],
                "answer": 1,
                "difficulty": "easy",
                "exam_type": "CBSE 12"
            },
            
            # CBSE 12 - Medium Questions
            {
                "text": "The limit of (sin x)/x as x approaches 0 is:",
                "options": ["0", "1", "∞", "undefined"],
                "answer": 1,
                "difficulty": "medium",
                "exam_type": "CBSE 12"
            },
            {
                "text": "In an AC circuit, the phase difference between voltage and current in a pure capacitor is:",
                "options": ["0°", "90°", "180°", "270°"],
                "answer": 1,
                "difficulty": "medium",
                "exam_type": "CBSE 12"
            },
            
            # CBSE 12 - Tough Questions
            {
                "text": "The magnetic field at the center of a current carrying circular loop of radius R carrying current I is:",
                "options": ["μ₀I/2R", "μ₀I/4πR", "μ₀I/2πR", "μ₀IR/2"],
                "answer": 0,
                "difficulty": "tough",
                "exam_type": "CBSE 12"
            },
            
            # JEE Main - Easy Questions
            {
                "text": "The number of significant figures in 0.00230 is:",
                "options": ["2", "3", "4", "5"],
                "answer": 1,
                "difficulty": "easy",
                "exam_type": "JEE Main"
            },
            {
                "text": "Which of the following is the weakest acid?",
                "options": ["HCl", "HNO₃", "CH₃COOH", "H₂SO₄"],
                "answer": 2,
                "difficulty": "easy",
                "exam_type": "JEE Main"
            },
            {
                "text": "The value of log₁₀(100) is:",
                "options": ["1", "2", "10", "100"],
                "answer": 1,
                "difficulty": "easy",
                "exam_type": "JEE Main"
            },
            {
                "text": "What is the molecular formula of glucose?",
                "options": ["C₆H₁₂O₆", "C₁₂H₂₂O₁₁", "C₂H₅OH", "CH₄"],
                "answer": 0,
                "difficulty": "easy",
                "exam_type": "JEE Main"
            },
            {
                "text": "The square root of 144 is:",
                "options": ["11", "12", "13", "14"],
                "answer": 1,
                "difficulty": "easy",
                "exam_type": "JEE Main"
            },
            
            # JEE Main - Medium Questions
            {
                "text": "If the roots of ax² + bx + c = 0 are α and β, then α + β equals:",
                "options": ["-b/a", "b/a", "-c/a", "c/a"],
                "answer": 0,
                "difficulty": "medium",
                "exam_type": "JEE Main"
            },
            {
                "text": "The hybridization of carbon in methane (CH₄) is:",
                "options": ["sp", "sp²", "sp³", "sp³d"],
                "answer": 2,
                "difficulty": "medium",
                "exam_type": "JEE Main"
            },
            
            # JEE Main - Tough Questions
            {
                "text": "A particle moves along x-axis such that its position is given by x = 2t³ - 3t² + 1. The acceleration at t = 2s is:",
                "options": ["18 m/s²", "12 m/s²", "6 m/s²", "24 m/s²"],
                "answer": 0,
                "difficulty": "tough",
                "exam_type": "JEE Main",
                "hint": "Use the second derivative of position to find acceleration"
            },
            {
                "text": "The number of unpaired electrons in Mn²⁺ ion is:",
                "options": ["3", "4", "5", "6"],
                "answer": 2,
                "difficulty": "tough",
                "exam_type": "JEE Main",
                "hint": "Consider the electronic configuration of Mn and the effect of losing 2 electrons"
            },
            
            # JEE Advanced - Tough Questions
            {
                "text": "A uniform magnetic field B exists in a cylindrical region. An electron enters the field perpendicularly. The radius of its circular path is:",
                "options": ["mv/eB", "eB/mv", "mvB/e", "e/mvB"],
                "answer": 0,
                "difficulty": "tough",
                "exam_type": "JEE Advanced",
                "hint": "Apply the Lorentz force formula and centripetal force condition"
            },
            {
                "text": "The integral ∫[0 to π/2] sin²x dx equals:",
                "options": ["π/4", "π/2", "1", "π"],
                "answer": 0,
                "difficulty": "tough",
                "exam_type": "JEE Advanced",
                "hint": "Use the identity sin²x = (1 - cos2x)/2"
            },
            {
                "text": "In the reaction 2A + B → 3C, if the rate of formation of C is 0.3 mol/L·s, what is the rate of consumption of A?",
                "options": ["0.1 mol/L·s", "0.2 mol/L·s", "0.45 mol/L·s", "0.6 mol/L·s"],
                "answer": 1,
                "difficulty": "tough",
                "exam_type": "JEE Advanced",
                "hint": "Use stoichiometric relationships in rate expressions"
            }
        ]
        
        print(f"🎯 Adding {len(questions_data)} comprehensive questions...")
        
        # Add questions to database
        added_count = 0
        for q_data in questions_data:
            # Check if question already exists
            existing = QuizQuestion.query.filter_by(text=q_data['text']).first()
            if not existing:
                question = QuizQuestion(
                    text=q_data['text'],
                    options=q_data['options'],
                    answer=q_data['answer'],
                    difficulty=q_data['difficulty'],
                    exam_type=q_data['exam_type'],
                    hint=q_data.get('hint')
                )
                db.session.add(question)
                added_count += 1
            else:
                print(f"⚠️ Question already exists: {q_data['text'][:50]}...")
        
        try:
            db.session.commit()
            print(f"✅ Successfully added {added_count} new questions!")
            
            # Print summary
            total_questions = QuizQuestion.query.count()
            print(f"📊 Database now contains {total_questions} total questions")
            
            # Print breakdown by exam type and difficulty
            for exam_type in ['CBSE 11', 'CBSE 12', 'JEE Main', 'JEE Advanced']:
                for difficulty in ['easy', 'medium', 'tough']:
                    count = QuizQuestion.query.filter_by(
                        exam_type=exam_type,
                        difficulty=difficulty,
                        is_active=True
                    ).count()
                    if count > 0:
                        print(f"   {exam_type} ({difficulty}): {count} questions")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Failed to add questions: {str(e)}")

if __name__ == "__main__":
    populate_questions()