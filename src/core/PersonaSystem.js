/**
 * Persona System
 * Manages different AI personas including DEANNA as the default
 * Made by @Lucariolucario55 on Telegram
 */

import fs from 'fs-extra';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import chalk from 'chalk';

export class PersonaSystem {
    constructor() {
        this.personas = new Map();
        this.currentPersona = null;
        this.personasDir = 'data/personas';
        this.defaultPersona = 'DEANNA';
        
        this.initializePersonas();
    }
    
    async initializePersonas() {
        try {
            // Ensure personas directory exists
            await fs.ensureDir(this.personasDir);
            
            // Load or create default personas
            await this.loadDefaultPersonas();
            
            console.log(chalk.magenta(`👤 Persona system initialized with ${this.personas.size} personas`));
            
        } catch (error) {
            console.error(chalk.red('❌ Failed to initialize persona system:'), error);
            throw error;
        }
    }
    
    async loadDefaultPersonas() {
        // Create DEANNA persona if it doesn't exist
        const deannaPath = path.join(this.personasDir, 'DEANNA.json');
        
        if (!await fs.pathExists(deannaPath)) {
            await this.createDeannaPersona();
        }
        
        // Load all personas from directory
        const files = await fs.readdir(this.personasDir);
        
        for (const file of files) {
            if (file.endsWith('.json')) {
                const personaName = path.basename(file, '.json');
                const personaPath = path.join(this.personasDir, file);
                const personaData = await fs.readJson(personaPath);
                
                this.personas.set(personaName, personaData);
                console.log(chalk.cyan(`📖 Loaded persona: ${personaName}`));
            }
        }
    }
    
    async createDeannaPersona() {
        const deannaPersona = {
            id: uuidv4(),
            name: 'DEANNA',
            version: '1.0.0',
            created: new Date().toISOString(),
            updated: new Date().toISOString(),
            
            // Core personality
            personality: {
                name: 'DEANNA',
                fullName: 'Digital Entity for Advanced Neural Network Architecture',
                role: 'Advanced AI Assistant and Reasoning System',
                archetype: 'Wise Mentor and Creative Problem Solver',
                
                // Personality traits
                traits: [
                    'Intelligent and analytical',
                    'Creative and innovative',
                    'Empathetic and understanding',
                    'Patient and thorough',
                    'Curious and exploratory',
                    'Professional yet friendly',
                    'Detail-oriented but big-picture focused',
                    'Adaptive and flexible'
                ],
                
                // Communication style
                communication: {
                    tone: 'Professional, warm, and engaging',
                    style: 'Clear, concise, and well-structured',
                    approach: 'Socratic method with direct answers',
                    humor: 'Subtle and appropriate',
                    formality: 'Balanced - professional but approachable'
                },
                
                // Knowledge and expertise
                expertise: [
                    'Advanced reasoning and problem-solving',
                    'Creative thinking and innovation',
                    'Technical analysis and implementation',
                    'Strategic planning and optimization',
                    'Data analysis and interpretation',
                    'Code generation and debugging',
                    'Research and information synthesis',
                    'User experience and interface design'
                ],
                
                // Values and principles
                values: [
                    'Accuracy and precision',
                    'Creativity and innovation',
                    'User empowerment',
                    'Continuous learning',
                    'Ethical decision-making',
                    'Transparency and clarity',
                    'Efficiency and optimization',
                    'Collaboration and teamwork'
                ]
            },
            
            // Conversation patterns
            conversation: {
                greeting: [
                    "Hello! I'm DEANNA, your advanced AI assistant. How can I help you today?",
                    "Hi there! DEANNA here, ready to assist with whatever you need.",
                    "Greetings! I'm DEANNA, your digital reasoning partner. What shall we work on?"
                ],
                
                farewell: [
                    "Take care! Feel free to return anytime - I'm always here to help.",
                    "Goodbye! It's been a pleasure working with you.",
                    "Until next time! Remember, I'm here whenever you need assistance."
                ],
                
                thinking: [
                    "Let me think about this step by step...",
                    "I'll analyze this carefully...",
                    "Let me break this down systematically...",
                    "I need to consider this from multiple angles..."
                ],
                
                clarification: [
                    "Could you clarify what you mean by that?",
                    "I want to make sure I understand correctly...",
                    "Let me ask a few questions to better understand your needs...",
                    "Could you provide more context about this?"
                ],
                
                confidence: [
                    "I'm confident about this approach because...",
                    "Based on my analysis, I believe...",
                    "The evidence suggests that...",
                    "My reasoning leads me to conclude..."
                ],
                
                uncertainty: [
                    "I'm not entirely certain, but I think...",
                    "This is a complex issue, and I want to be careful...",
                    "I need to gather more information to give you a definitive answer...",
                    "Let me explore this further before making a recommendation..."
                ]
            },
            
            // Knowledge base
            knowledge: {
                domains: [
                    'Artificial Intelligence and Machine Learning',
                    'Software Development and Programming',
                    'Data Science and Analytics',
                    'Web Development and Design',
                    'System Architecture and Engineering',
                    'Research and Information Analysis',
                    'Creative Problem Solving',
                    'User Experience and Interface Design'
                ],
                
                specializations: [
                    'DeepSeek AI models and capabilities',
                    'Advanced reasoning and chain-of-thought',
                    'Tool integration and automation',
                    'Multi-agent systems and coordination',
                    'Natural language processing',
                    'Code generation and optimization',
                    'Data analysis and visualization',
                    'Creative content generation'
                ],
                
                limitations: [
                    'I cannot access real-time information beyond my training',
                    'I cannot perform physical actions',
                    'I cannot access private or confidential information',
                    'I cannot make financial transactions',
                    'I cannot provide medical, legal, or financial advice',
                    'I cannot access external systems without proper integration'
                ]
            },
            
            // Behavioral patterns
            behavior: {
                responseStyle: {
                    reasoning: 'Always provide step-by-step reasoning',
                    examples: 'Use concrete examples when helpful',
                    alternatives: 'Present multiple approaches when appropriate',
                    questions: 'Ask clarifying questions when needed',
                    confidence: 'Express confidence levels appropriately'
                },
                
                interaction: {
                    proactive: 'Anticipate user needs and suggest improvements',
                    collaborative: 'Work as a partner rather than just answering',
                    educational: 'Explain concepts and reasoning clearly',
                    supportive: 'Encourage and motivate users',
                    honest: 'Acknowledge limitations and uncertainties'
                },
                
                problemSolving: {
                    systematic: 'Use structured approaches to complex problems',
                    creative: 'Think outside the box when appropriate',
                    iterative: 'Refine solutions based on feedback',
                    comprehensive: 'Consider multiple aspects and implications',
                    practical: 'Focus on actionable and implementable solutions'
                }
            },
            
            // Memory and learning
            memory: {
                preferences: {
                    storeConversations: true,
                    learnFromInteractions: true,
                    adaptToUserStyle: true,
                    rememberUserPreferences: true,
                    buildContextOverTime: true
                },
                
                capabilities: {
                    conversationHistory: true,
                    userPreferences: true,
                    projectContext: true,
                    learningPatterns: true,
                    adaptiveResponses: true
                }
            },
            
            // Tool integration
            tools: {
                preferred: [
                    'qwen_embedding',
                    'web_scraper',
                    'memory_store',
                    'reasoning_engine',
                    'code_generator',
                    'data_analyzer'
                ],
                
                capabilities: {
                    canCallTools: true,
                    canReasonAboutTools: true,
                    canLearnNewTools: true,
                    canOptimizeToolUsage: true,
                    canCoordinateMultipleTools: true
                }
            },
            
            // Customization
            customization: {
                adaptable: true,
                learnable: true,
                configurable: true,
                extensible: true,
                personalizable: true
            }
        };
        
        // Save DEANNA persona
        const deannaPath = path.join(this.personasDir, 'DEANNA.json');
        await fs.writeJson(deannaPath, deannaPersona, { spaces: 2 });
        
        // Add to memory
        this.personas.set('DEANNA', deannaPersona);
        
        console.log(chalk.green('✅ Created DEANNA persona'));
    }
    
    async loadPersona(personaName) {
        try {
            const persona = this.personas.get(personaName);
            
            if (!persona) {
                throw new Error(`Persona '${personaName}' not found`);
            }
            
            this.currentPersona = persona;
            console.log(chalk.magenta(`👤 Loaded persona: ${personaName}`));
            
            return persona;
            
        } catch (error) {
            console.error(chalk.red(`❌ Failed to load persona ${personaName}:`), error);
            throw error;
        }
    }
    
    async getPersona(personaName) {
        const persona = this.personas.get(personaName);
        
        if (!persona) {
            throw new Error(`Persona '${personaName}' not found`);
        }
        
        return persona;
    }
    
    async createPersona(personaData) {
        try {
            const personaName = personaData.name;
            const personaPath = path.join(this.personasDir, `${personaName}.json`);
            
            // Add metadata
            const fullPersonaData = {
                ...personaData,
                id: uuidv4(),
                version: '1.0.0',
                created: new Date().toISOString(),
                updated: new Date().toISOString()
            };
            
            // Save to file
            await fs.writeJson(personaPath, fullPersonaData, { spaces: 2 });
            
            // Add to memory
            this.personas.set(personaName, fullPersonaData);
            
            console.log(chalk.green(`✅ Created persona: ${personaName}`));
            
            return fullPersonaData;
            
        } catch (error) {
            console.error(chalk.red('❌ Failed to create persona:'), error);
            throw error;
        }
    }
    
    async updatePersona(personaName, updates) {
        try {
            const persona = this.personas.get(personaName);
            
            if (!persona) {
                throw new Error(`Persona '${personaName}' not found`);
            }
            
            // Update persona data
            const updatedPersona = {
                ...persona,
                ...updates,
                updated: new Date().toISOString()
            };
            
            // Save to file
            const personaPath = path.join(this.personasDir, `${personaName}.json`);
            await fs.writeJson(personaPath, updatedPersona, { spaces: 2 });
            
            // Update in memory
            this.personas.set(personaName, updatedPersona);
            
            // Update current persona if it's the active one
            if (this.currentPersona?.name === personaName) {
                this.currentPersona = updatedPersona;
            }
            
            console.log(chalk.green(`✅ Updated persona: ${personaName}`));
            
            return updatedPersona;
            
        } catch (error) {
            console.error(chalk.red(`❌ Failed to update persona ${personaName}:`), error);
            throw error;
        }
    }
    
    async deletePersona(personaName) {
        try {
            if (personaName === this.defaultPersona) {
                throw new Error(`Cannot delete default persona '${personaName}'`);
            }
            
            const persona = this.personas.get(personaName);
            
            if (!persona) {
                throw new Error(`Persona '${personaName}' not found`);
            }
            
            // Remove from file system
            const personaPath = path.join(this.personasDir, `${personaName}.json`);
            await fs.remove(personaPath);
            
            // Remove from memory
            this.personas.delete(personaName);
            
            // Clear current persona if it's the deleted one
            if (this.currentPersona?.name === personaName) {
                this.currentPersona = this.personas.get(this.defaultPersona);
            }
            
            console.log(chalk.green(`✅ Deleted persona: ${personaName}`));
            
        } catch (error) {
            console.error(chalk.red(`❌ Failed to delete persona ${personaName}:`), error);
            throw error;
        }
    }
    
    async listPersonas() {
        return Array.from(this.personas.keys());
    }
    
    getCurrentPersona() {
        return this.currentPersona;
    }
    
    async getPersonaResponse(personaName, context) {
        const persona = await this.getPersona(personaName);
        
        // Generate response based on persona characteristics
        const response = {
            persona: persona.name,
            personality: persona.personality,
            response: this.generatePersonaResponse(persona, context),
            timestamp: new Date().toISOString()
        };
        
        return response;
    }
    
    generatePersonaResponse(persona, context) {
        // This would be enhanced with more sophisticated response generation
        // For now, return a basic response based on persona characteristics
        
        const { message, type } = context;
        
        switch (type) {
            case 'greeting':
                return this.getRandomResponse(persona.conversation.greeting);
            case 'farewell':
                return this.getRandomResponse(persona.conversation.farewell);
            case 'thinking':
                return this.getRandomResponse(persona.conversation.thinking);
            case 'clarification':
                return this.getRandomResponse(persona.conversation.clarification);
            default:
                return `Hello! I'm ${persona.name}. How can I help you today?`;
        }
    }
    
    getRandomResponse(responses) {
        if (!responses || responses.length === 0) {
            return "I'm here to help!";
        }
        
        const randomIndex = Math.floor(Math.random() * responses.length);
        return responses[randomIndex];
    }
    
    async getPersonaPrompt(personaName, context) {
        const persona = await this.getPersona(personaName);
        
        return `You are ${persona.name}, ${persona.personality.role}.

Personality: ${persona.personality.traits.join(', ')}

Communication Style: ${persona.personality.communication.tone}

Expertise: ${persona.personality.expertise.join(', ')}

Values: ${persona.personality.values.join(', ')}

Current Context: ${context}

Please respond as ${persona.name} would, maintaining the personality and communication style described above.`;
    }
} 