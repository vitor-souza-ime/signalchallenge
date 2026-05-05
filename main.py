import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  SafeAreaView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

// ─── API Configuration ────────────────────────────────────────────────────────
const OPENROUTER_KEY =
  'SUA_API_KEY_AQUI';          // ← paste your key here
const OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions';
const MODEL          = 'mistralai/mistral-large-2407';

// ─── Topics ───────────────────────────────────────────────────────────────────
const TOPICS = [
  // Communications & Networks
  'Antennas, Propagation and Microwaves',
  'Machine Learning in Communications',
  'Optical Communications and Networks, Optoelectronics and Photonics',
  'Wireless Communications and Networks',
  'Quantum Communications',
  'Ultra-Reliable Low-Latency Communications (URLLC)',
  'Satellite Communications',
  'Power Line Communications',
  'Communications Education',
  'Applied Electromagnetism',
  'Internet of Things (IoT)',
  'Telecommunications Device Design and Implementation',
  'Cognitive Radio',
  'Computer and Sensor Networks',
  '5G, B5G and 6G Networks',
  'Cybersecurity',
  'Communication Services and Systems',
  'Information Theory and Coding',
  'Communications Theory',
  // Signal Processing
  'Compressive Sampling and Sensing',
  'Machine Learning in Signal Processing',
  'Forensic Science, Cryptography and Security',
  'Data Science',
  'Digital Signal Processing Systems Design and Implementation',
  'Signal Processing Education',
  'Audio and Speech Processing',
  'Image and Video Processing',
  'Acoustic Signal Processing',
  'Biomedical Signal and Image Processing',
  'Signal Processing for Smart Grids',
  'Graph Signal Processing',
  'Signal Processing for Power Systems',
  'Signal Processing for Mechanical Systems',
  'Signal Processing for Navigation and Localization',
  'Signal Processing for Remote Sensing and Geophysics',
  'Adaptive, Sensor Array and Multichannel Signal Processing',
  'Sparse Representations',
];

// ─── Difficulty palette ───────────────────────────────────────────────────────
const LEVELS = [
  { label: 'Foundational', icon: '📡', key: 'Easy',   grad: ['#00c6fb', '#005bea'] },
  { label: 'Advanced',     icon: '🛰️', key: 'Medium', grad: ['#f7971e', '#ffd200'] },
  { label: 'Expert',       icon: '⚡', key: 'Hard',   grad: ['#f953c6', '#b91d73'] },
];

// ─── Prompt builder ───────────────────────────────────────────────────────────
const buildPrompt = (level, topic) => `
You are a telecommunications and signal processing question generator.

RETURN ONLY PURE JSON, NO EXTRA TEXT.

Generate exactly 1 (one) multiple choice question IN ENGLISH.
The question must have 5 alternatives, with ONLY 1 correct answer.

Mandatory JSON format:
{
  "question": "question text",
  "options": ["A","B","C","D","E"],
  "correct_index": 0-4
}

Mandatory topic: ${topic}
Level: ${level}

No explanations, comments or markdown allowed.
Return ONLY the JSON, nothing else.
`;

// ─── Fetch a single question ──────────────────────────────────────────────────
async function requestQuestion(prompt) {
  try {
    const resp = await fetch(OPENROUTER_URL, {
      method: 'POST',
      headers: {
        'Content-Type':  'application/json',
        Authorization:   `Bearer ${OPENROUTER_KEY}`,
        'HTTP-Referer':  'https://snack.expo.dev',
        'X-Title':       'Telecom Quiz App',
      },
      body: JSON.stringify({
        model: MODEL,
        messages: [
          { role: 'system', content: 'Answer only with valid JSON.' },
          { role: 'user',   content: prompt },
        ],
        max_tokens: 300,
        temperature: 0.2,
      }),
    });

    const data    = await resp.json();
    const content = data?.choices?.[0]?.message?.content;
    if (!content) return null;

    const match = content.match(/\{[\s\S]*\}/);
    if (!match)  return null;

    const parsed = JSON.parse(match[0]);
    if (
      parsed.question &&
      Array.isArray(parsed.options) &&
      parsed.options.length === 5 &&
      typeof parsed.correct_index === 'number'
    ) {
      return parsed;
    }
    return null;
  } catch {
    return null;
  }
}

const fallback = (topic, i) => ({
  question:      `[Fallback] Question ${i + 1} about "${topic}"`,
  options:       ['Option A', 'Option B', 'Option C', 'Option D', 'Option E'],
  correct_index: 0,
});

// ─── Shuffle options while tracking correct answer ────────────────────────────
function shuffleOptions(q) {
  // Build indexed pairs, shuffle with Fisher-Yates, remap correct_index
  const pairs = q.options.map((text, i) => ({ text, isCorrect: i === q.correct_index }));
  for (let i = pairs.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [pairs[i], pairs[j]] = [pairs[j], pairs[i]];
  }
  return {
    ...q,
    options:       pairs.map((p) => p.text),
    correct_index: pairs.findIndex((p) => p.isCorrect),
  };
}

// ─── Small reusable gradient button ──────────────────────────────────────────
function GradBtn({ grad, onPress, children, style }) {
  return (
    <TouchableOpacity onPress={onPress} activeOpacity={0.85} style={style}>
      <LinearGradient colors={grad} style={styles.gradBtnInner} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }}>
        {children}
      </LinearGradient>
    </TouchableOpacity>
  );
}

// ─── App ──────────────────────────────────────────────────────────────────────
export default function App() {
  const [phase,          setPhase]          = useState('menu');
  const [difficulty,     setDifficulty]     = useState(null);
  const [loadingMsg,     setLoadingMsg]     = useState('');
  const [questions,      setQuestions]      = useState([]);
  const [currentIndex,   setCurrentIndex]   = useState(0);
  const [selectedOption, setSelectedOption] = useState(null);
  const [score,          setScore]          = useState(0);

  // ── Start quiz ──────────────────────────────────────────────────────────────
  const startQuiz = async (level) => {
    setDifficulty(level);
    setPhase('loading');
    setScore(0);
    setSelectedOption(null);

    const qList = [];
    for (let i = 0; i < 10; i++) {
      setLoadingMsg(`Generating question ${i + 1} of 10…`);
      const topic = TOPICS[Math.floor(Math.random() * TOPICS.length)];
      const q     = await requestQuestion(buildPrompt(level, topic));
      qList.push(shuffleOptions(q || fallback(topic, i)));
    }

    setQuestions(qList);
    setCurrentIndex(0);
    setPhase('quiz');
  };

  // ── Answer selection ────────────────────────────────────────────────────────
  const handleSelect = (i) => {
    setSelectedOption(i);
    if (i === questions[currentIndex].correct_index) {
      setScore((s) => s + 1);
    }
  };

  const next = () => {
    if (currentIndex + 1 >= questions.length) setPhase('result');
    else setCurrentIndex((c) => c + 1);
    setSelectedOption(null);
  };

  const reset = () => {
    setPhase('menu');
    setQuestions([]);
    setScore(0);
  };

  // ── Result copy ─────────────────────────────────────────────────────────────
  const pct = (score / 10) * 100;
  const resultMeta =
    pct >= 90 ? { icon: '🏆', label: 'Outstanding signal!' } :
    pct >= 70 ? { icon: '📶', label: 'Strong reception!'   } :
    pct >= 50 ? { icon: '📡', label: 'Signal acquired!'    } :
                { icon: '🔇', label: 'Boost your bandwidth' };

  // ═══════════════════════════════════════════════════════════════════════════
  //  MENU
  // ═══════════════════════════════════════════════════════════════════════════
  if (phase === 'menu') {
    return (
      <LinearGradient colors={['#0a0e27', '#0d1b4b', '#0a2a6e']} style={styles.fill}>
        <SafeAreaView style={styles.fill}>
          <ScrollView contentContainerStyle={styles.menuScroll}>
            {/* Header */}
            <View style={styles.menuHeader}>
              <View style={styles.signalRow}>
                {[1, 2, 3, 4].map((h) => (
                  <View key={h} style={[styles.signalBar, { height: h * 8 }]} />
                ))}
              </View>
              <Text style={styles.appTag}>TELECOM QUIZ</Text>
              <Text style={styles.appTitle}>Signal{'\n'}Challenge</Text>
              <Text style={styles.appSub}>
                Test your knowledge across{'\n'}Telecommunications &amp; Signal Processing
              </Text>
            </View>

            {/* Divider */}
            <View style={styles.divider} />
            <Text style={styles.chooseLabel}>SELECT DIFFICULTY</Text>

            {/* Level buttons */}
            <View style={styles.levelList}>
              {LEVELS.map((lv) => (
                <GradBtn
                  key={lv.key}
                  grad={lv.grad}
                  onPress={() => startQuiz(lv.key)}
                  style={styles.levelBtnWrap}
                >
                  <View style={styles.levelBtnContent}>
                    <Text style={styles.levelIcon}>{lv.icon}</Text>
                    <View>
                      <Text style={styles.levelLabel}>{lv.label}</Text>
                      <Text style={styles.levelSub}>{lv.key}</Text>
                    </View>
                    <Text style={styles.levelArrow}>›</Text>
                  </View>
                </GradBtn>
              ))}
            </View>

            <Text style={styles.footNote}>37 topics · 10 questions per round</Text>
          </ScrollView>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  //  LOADING
  // ═══════════════════════════════════════════════════════════════════════════
  if (phase === 'loading') {
    const pctDone = parseInt(loadingMsg.match(/\d+/)?.[0] || '0');
    const bar     = Math.round((pctDone / 10) * 100);
    return (
      <LinearGradient colors={['#0a0e27', '#0d1b4b', '#0a2a6e']} style={styles.fill}>
        <SafeAreaView style={[styles.fill, styles.center]}>
          <ActivityIndicator size="large" color="#00c6fb" />
          <Text style={styles.loadTitle}>Building your quiz…</Text>
          <Text style={styles.loadMsg}>{loadingMsg}</Text>
          <View style={styles.loadBarBg}>
            <View style={[styles.loadBarFill, { width: `${bar}%` }]} />
          </View>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  //  QUIZ
  // ═══════════════════════════════════════════════════════════════════════════
  if (phase === 'quiz') {
    const q        = questions[currentIndex];
    const progress = ((currentIndex + 1) / 10) * 100;

    return (
      <LinearGradient colors={['#0a0e27', '#0d1b4b', '#0a2a6e']} style={styles.fill}>
        <SafeAreaView style={styles.fill}>
          <ScrollView contentContainerStyle={styles.quizScroll}>

            {/* Progress */}
            <View style={styles.quizTop}>
              <Text style={styles.quizCounter}>
                Q{currentIndex + 1}
                <Text style={styles.quizCounterDim}> / 10</Text>
              </Text>
              <Text style={styles.quizScore}>⚡ {score}</Text>
            </View>
            <View style={styles.progBg}>
              <LinearGradient
                colors={['#00c6fb', '#005bea']}
                style={[styles.progFill, { width: `${progress}%` }]}
                start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
              />
            </View>

            {/* Difficulty badge */}
            <View style={styles.badgeRow}>
              <View style={styles.badge}>
                <Text style={styles.badgeText}>{difficulty.toUpperCase()}</Text>
              </View>
            </View>

            {/* Question card */}
            <View style={styles.qCard}>
              <Text style={styles.qText}>{q.question}</Text>
            </View>

            {/* Options */}
            {q.options.map((opt, i) => {
              const isCorrect  = q.correct_index === i;
              const isSelected = selectedOption === i;
              const revealed   = selectedOption !== null;

              let bg      = 'rgba(255,255,255,0.06)';
              let border  = 'rgba(255,255,255,0.15)';
              let txtClr  = '#d0e8ff';
              let letClr  = '#7ab8f5';

              if (revealed) {
                if (isCorrect) {
                  bg = 'rgba(0,255,140,0.12)'; border = '#00ff8c'; txtClr = '#e0fff3'; letClr = '#00ff8c';
                } else if (isSelected) {
                  bg = 'rgba(255,60,80,0.12)';  border = '#ff3c50'; txtClr = '#ffe0e4'; letClr = '#ff3c50';
                }
              }

              return (
                <TouchableOpacity
                  key={i}
                  disabled={revealed}
                  onPress={() => handleSelect(i)}
                  style={[styles.optBtn, { backgroundColor: bg, borderColor: border }]}
                  activeOpacity={0.75}
                >
                  <View style={[styles.optLetter, { borderColor: letClr }]}>
                    <Text style={[styles.optLetterTxt, { color: letClr }]}>
                      {String.fromCharCode(65 + i)}
                    </Text>
                  </View>
                  <Text style={[styles.optTxt, { color: txtClr }]}>{opt}</Text>
                  {revealed && isCorrect && <Text style={styles.checkmark}>✓</Text>}
                  {revealed && isSelected && !isCorrect && <Text style={styles.crossmark}>✗</Text>}
                </TouchableOpacity>
              );
            })}

            {/* Next button */}
            {selectedOption !== null && (
              <GradBtn
                grad={['#00c6fb', '#005bea']}
                onPress={next}
                style={styles.nextWrap}
              >
                <Text style={styles.nextTxt}>
                  {currentIndex + 1 >= 10 ? 'View Results  🏁' : 'Next Question  →'}
                </Text>
              </GradBtn>
            )}

            <View style={{ height: 30 }} />
          </ScrollView>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  //  RESULT
  // ═══════════════════════════════════════════════════════════════════════════
  if (phase === 'result') {
    return (
      <LinearGradient colors={['#0a0e27', '#0d1b4b', '#0a2a6e']} style={styles.fill}>
        <SafeAreaView style={[styles.fill, styles.center]}>
          <Text style={styles.resIcon}>{resultMeta.icon}</Text>
          <Text style={styles.resLabel}>{resultMeta.label}</Text>

          {/* Score ring */}
          <View style={styles.scoreRing}>
            <LinearGradient
              colors={pct >= 70 ? ['#00c6fb', '#005bea'] : ['#f953c6', '#b91d73']}
              style={styles.scoreRingInner}
            >
              <Text style={styles.scoreNum}>{score}</Text>
              <Text style={styles.scoreDen}>/10</Text>
            </LinearGradient>
          </View>

          <Text style={styles.resPct}>{pct.toFixed(0)}% correct</Text>

          {/* Breakdown bar */}
          <View style={styles.breakdownBg}>
            <LinearGradient
              colors={pct >= 70 ? ['#00c6fb', '#005bea'] : ['#f953c6', '#b91d73']}
              style={[styles.breakdownFill, { width: `${pct}%` }]}
              start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
            />
          </View>

          <GradBtn grad={['#00c6fb', '#005bea']} onPress={reset} style={styles.playAgainWrap}>
            <Text style={styles.playAgainTxt}>🔄  Play Again</Text>
          </GradBtn>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  return null;
}

// ─── Styles ───────────────────────────────────────────────────────────────────
const styles = StyleSheet.create({
  fill:   { flex: 1 },
  center: { justifyContent: 'center', alignItems: 'center', paddingHorizontal: 24 },

  // ── Gradient button
  gradBtnInner: {
    borderRadius: 14,
    overflow: 'hidden',
  },

  // ── Menu
  menuScroll: {
    paddingHorizontal: 24,
    paddingBottom: 40,
    alignItems: 'center',
  },
  menuHeader: {
    alignItems: 'center',
    paddingTop: 50,
    marginBottom: 36,
  },
  signalRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 5,
    marginBottom: 20,
  },
  signalBar: {
    width: 8,
    borderRadius: 3,
    backgroundColor: '#00c6fb',
  },
  appTag: {
    fontFamily:    'monospace',
    fontSize:      11,
    letterSpacing: 6,
    color:         '#00c6fb',
    marginBottom:  12,
  },
  appTitle: {
    fontSize:    52,
    fontWeight:  '900',
    color:       '#ffffff',
    textAlign:   'center',
    lineHeight:  56,
    marginBottom: 14,
  },
  appSub: {
    fontSize:   15,
    color:      '#7ab8f5',
    textAlign:  'center',
    lineHeight: 22,
  },
  divider: {
    width:           '80%',
    height:          1,
    backgroundColor: 'rgba(122,184,245,0.2)',
    marginBottom:    24,
  },
  chooseLabel: {
    fontFamily:    'monospace',
    fontSize:      11,
    letterSpacing: 4,
    color:         '#7ab8f5',
    marginBottom:  16,
  },
  levelList: {
    width:    '100%',
    maxWidth: 420,
    gap:      14,
  },
  levelBtnWrap: { borderRadius: 14 },
  levelBtnContent: {
    flexDirection:  'row',
    alignItems:     'center',
    paddingVertical:  18,
    paddingHorizontal: 20,
    gap: 16,
  },
  levelIcon:  { fontSize: 28 },
  levelLabel: { fontSize: 18, fontWeight: '700', color: '#fff' },
  levelSub:   { fontSize: 12, color: 'rgba(255,255,255,0.7)', marginTop: 2 },
  levelArrow: { fontSize: 28, color: 'rgba(255,255,255,0.6)', marginLeft: 'auto' },
  footNote: {
    marginTop:  32,
    fontSize:   13,
    color:      'rgba(122,184,245,0.5)',
    fontFamily: 'monospace',
  },

  // ── Loading
  loadTitle: {
    fontSize:    22,
    fontWeight:  '700',
    color:       '#fff',
    marginTop:   20,
    marginBottom: 8,
  },
  loadMsg: { fontSize: 14, color: '#7ab8f5', marginBottom: 24 },
  loadBarBg: {
    width:           260,
    height:          6,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius:    6,
    overflow:        'hidden',
  },
  loadBarFill: {
    height:          '100%',
    backgroundColor: '#00c6fb',
    borderRadius:    6,
  },

  // ── Quiz
  quizScroll: { paddingHorizontal: 20, paddingTop: 20 },
  quizTop: {
    flexDirection:  'row',
    justifyContent: 'space-between',
    alignItems:     'center',
    marginBottom:   12,
  },
  quizCounter:    { fontSize: 22, fontWeight: '800', color: '#ffffff' },
  quizCounterDim: { fontWeight: '400', color: '#7ab8f5' },
  quizScore:      { fontSize: 18, fontWeight: '700', color: '#ffd200' },
  progBg: {
    height:          6,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius:    6,
    overflow:        'hidden',
    marginBottom:    16,
  },
  progFill: { height: '100%', borderRadius: 6 },
  badgeRow: { marginBottom: 12 },
  badge: {
    alignSelf:       'flex-start',
    backgroundColor: 'rgba(0,198,251,0.15)',
    borderRadius:    6,
    borderWidth:     1,
    borderColor:     'rgba(0,198,251,0.4)',
    paddingVertical:  4,
    paddingHorizontal: 10,
  },
  badgeText: {
    fontFamily:    'monospace',
    fontSize:      10,
    letterSpacing: 3,
    color:         '#00c6fb',
  },
  qCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius:    18,
    borderWidth:     1,
    borderColor:     'rgba(255,255,255,0.1)',
    padding:         24,
    marginBottom:    20,
  },
  qText: { fontSize: 18, color: '#e8f4ff', lineHeight: 26 },
  optBtn: {
    flexDirection:  'row',
    alignItems:     'center',
    borderWidth:    1.5,
    borderRadius:   12,
    padding:        14,
    marginBottom:   10,
    gap:            12,
  },
  optLetter: {
    width:        32,
    height:       32,
    borderRadius: 16,
    borderWidth:  1.5,
    justifyContent: 'center',
    alignItems:     'center',
  },
  optLetterTxt: { fontSize: 14, fontWeight: '700' },
  optTxt:       { fontSize: 15, flex: 1, lineHeight: 21 },
  checkmark:    { fontSize: 18, color: '#00ff8c' },
  crossmark:    { fontSize: 18, color: '#ff3c50' },
  nextWrap:     { borderRadius: 14, marginTop: 4 },
  nextTxt: {
    fontSize:    17,
    fontWeight:  '700',
    color:       '#fff',
    textAlign:   'center',
    paddingVertical:  18,
  },

  // ── Result
  resIcon:  { fontSize: 80, marginBottom: 12 },
  resLabel: { fontSize: 22, fontWeight: '700', color: '#7ab8f5', marginBottom: 32 },
  scoreRing: {
    width:        160,
    height:       160,
    borderRadius: 80,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderWidth:  2,
    borderColor:  'rgba(0,198,251,0.3)',
    justifyContent: 'center',
    alignItems:     'center',
    marginBottom:   20,
  },
  scoreRingInner: {
    width:          144,
    height:         144,
    borderRadius:   72,
    justifyContent: 'center',
    alignItems:     'center',
  },
  scoreNum: { fontSize: 60, fontWeight: '900', color: '#fff' },
  scoreDen: { fontSize: 20, color: 'rgba(255,255,255,0.7)', marginTop: -8 },
  resPct:   { fontSize: 16, color: '#7ab8f5', marginBottom: 20 },
  breakdownBg: {
    width:           260,
    height:          8,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius:    8,
    overflow:        'hidden',
    marginBottom:    36,
  },
  breakdownFill: { height: '100%', borderRadius: 8 },
  playAgainWrap: { borderRadius: 14, minWidth: 200 },
  playAgainTxt: {
    fontSize:    18,
    fontWeight:  '700',
    color:       '#fff',
    textAlign:   'center',
    paddingVertical:   18,
    paddingHorizontal: 36,
  },
});
