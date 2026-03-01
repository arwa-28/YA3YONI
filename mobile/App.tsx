import React, {useState, useEffect, useRef} from 'react';
import {
  SafeAreaView,
  StyleSheet,
  Text,
  View,
  Image,
  TouchableOpacity,
  TextInput,
  Modal,
  ScrollView,
  Alert,
  Platform,
} from 'react-native';

const PRIMARY_COLOR = '#173c80';
const BUTTON_COLOR = '#4E6EF2';
const TEXT_COLOR = 'white';
const EYE_COLORS = ['blue', 'green', 'brown', 'gray', 'red'];
const EYE_QUOTES = [
  'Ocean',
  'Olive',
  'Almond',
  'Cloudy',
  "incase you're a vampire",
];
// Use 10.0.2.2 for Android emulator to access localhost, otherwise localhost
const API_URL = Platform.OS === 'android' ? 'http://10.0.2.2:8000/api' : 'http://localhost:8000/api';

const App = () => {
  const [screen, setScreen] = useState('Main');
  const [username, setUsername] = useState('stranger');
  const [eyeColor, setEyeColor] = useState('blue');
  const [isRunning, setIsRunning] = useState(false);
  const [showPopup, setShowPopup] = useState(false);
  const [countdown, setCountdown] = useState(20);
  const [statusMessage, setStatusMessage] = useState('');

  // Settings screen temporary state (must be at top level to follow Rules of Hooks)
  const [tempUsername, setTempUsername] = useState('stranger');
  const [tempEyeIndex, setTempEyeIndex] = useState(0);

  const timerRef = useRef(null);
  const syncRef = useRef(null);

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const response = await fetch(`${API_URL}/user/${username}/`);
      if (response.ok) {
        const data = await response.json();
        setEyeColor(data.eye_color);
        setTempUsername(username);
        setTempEyeIndex(EYE_COLORS.indexOf(data.eye_color));
      }
    } catch (error) {
      console.log('Error fetching user data', error);
    }
  };

  const syncWithBackend = async (incSeconds = 0, currentUsername = username, currentEyeColor = eyeColor) => {
    try {
      await fetch(`${API_URL}/sync/`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          username: currentUsername,
          eye_color: currentEyeColor,
          device_type: 'mobile',
          increment_seconds: incSeconds,
        }),
      });
    } catch (error) {
      console.log('Error syncing data', error);
    }
  };

  useEffect(() => {
    if (isRunning) {
      timerRef.current = setInterval(() => {
        setShowPopup(true);
        setCountdown(20);
      }, 20 * 60 * 1000); // 20 minutes

      syncRef.current = setInterval(() => {
        syncWithBackend(10);
      }, 10000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
      if (syncRef.current) clearInterval(syncRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (syncRef.current) clearInterval(syncRef.current);
    };
  }, [isRunning, username, eyeColor]);

  useEffect(() => {
    let cdTimer;
    if (showPopup && countdown > 0) {
      cdTimer = setTimeout(() => setCountdown(countdown - 1), 1000);
    } else if (countdown === 0) {
      setShowPopup(false);
    }
    return () => { if (cdTimer) clearTimeout(cdTimer); };
  }, [showPopup, countdown]);

  const handleStartStop = () => {
    if (!isRunning) {
      setIsRunning(true);
      setStatusMessage('');
    } else {
      setIsRunning(false);
      setStatusMessage("You'll come back crying soon..");
    }
  };

  const openSettings = () => {
    setTempUsername(username);
    setTempEyeIndex(EYE_COLORS.indexOf(eyeColor));
    setScreen('Settings');
  };

  const handleSaveSettings = () => {
    const newUsername = tempUsername.trim() || 'stranger';
    const newEyeColor = EYE_COLORS[tempEyeIndex];
    setUsername(newUsername);
    setEyeColor(newEyeColor);
    syncWithBackend(0, newUsername, newEyeColor);
    setScreen('Main');
    Alert.alert('Saved ✓');
  };

  const renderMain = () => (
    <View style={styles.container}>
      <Text style={styles.usernameText}>- {username} -</Text>
      <Image
        source={{uri: `https://raw.githubusercontent.com/arwa-28/YA3YONI/main/images/${eyeColor}.png`}}
        style={styles.eyeImage}
      />
      <TouchableOpacity style={styles.button} onPress={handleStartStop}>
        <Text style={styles.buttonText}>{isRunning ? 'STOP' : 'START'}</Text>
      </TouchableOpacity>
      <Text style={styles.statusText}>{statusMessage}</Text>
      <TouchableOpacity onPress={openSettings}>
        <Text style={styles.navText}>⚙️ Settings</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={() => setScreen('Info')}>
        <Text style={styles.navText}>? Info</Text>
      </TouchableOpacity>
    </View>
  );

  const renderSettings = () => (
    <View style={styles.container}>
      <TouchableOpacity style={styles.backButton} onPress={() => setScreen('Main')}>
        <Text style={styles.navText}>← Back</Text>
      </TouchableOpacity>
      <Text style={styles.label}>So, what should I call you?</Text>
      <TextInput
        style={styles.input}
        value={tempUsername}
        onChangeText={setTempUsername}
      />
      <Text style={styles.label}>Choose your eye color:</Text>
      <Image
        source={{uri: `https://raw.githubusercontent.com/arwa-28/YA3YONI/main/images/${EYE_COLORS[tempEyeIndex]}.png`}}
        style={styles.eyeImageSmall}
      />
      <Text style={styles.quoteText}>{EYE_QUOTES[tempEyeIndex]}</Text>
      <View style={styles.navRow}>
        <TouchableOpacity
          style={styles.smallButton}
          onPress={() => setTempEyeIndex((tempEyeIndex - 1 + EYE_COLORS.length) % EYE_COLORS.length)}>
          <Text style={styles.buttonTextSmall}>⬅ Prev</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.smallButton}
          onPress={() => setTempEyeIndex((tempEyeIndex + 1) % EYE_COLORS.length)}>
          <Text style={styles.buttonTextSmall}>Next ➡</Text>
        </TouchableOpacity>
      </View>
      <TouchableOpacity style={[styles.button, {backgroundColor: '#364B73'}]} onPress={handleSaveSettings}>
        <Text style={styles.buttonText}>💾 Save</Text>
      </TouchableOpacity>
    </View>
  );

  const renderInfo = () => (
    <ScrollView contentContainerStyle={styles.container}>
      <TouchableOpacity style={styles.backButton} onPress={() => setScreen('Main')}>
        <Text style={styles.navText}>← Back</Text>
      </TouchableOpacity>
      <Text style={styles.title}>Ya3yoni</Text>
      <Text style={styles.version}>Version 1.0</Text>
      <Text style={styles.infoText}>
        - this app was made for your deadly brain that forgets to blink, playing staring contests with your computer.{'\n\n'}
        And no, those 20 seconds of closing your eyes still won’t finish the task you’ve been avoiding until the deadline…
        but at least your eyes won’t suffer for it.{'\n\n'}
        So here I am solving a problem you didn’t even know you had.{'\n\n'}
        you’re welcome{'\n\n'}
        Credits: Arwa Mohamed
      </Text>
    </ScrollView>
  );

  return (
    <SafeAreaView style={{flex: 1, backgroundColor: PRIMARY_COLOR}}>
      {screen === 'Main' && renderMain()}
      {screen === 'Settings' && renderSettings()}
      {screen === 'Info' && renderInfo()}

      <Modal visible={showPopup} transparent animationType="fade">
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <Image
              source={{uri: 'https://raw.githubusercontent.com/arwa-28/YA3YONI/main/images/closed.png'}}
              style={styles.eyeImageSmall}
            />
            <Text style={styles.modalText}>🔔 Close your eyes!</Text>
            <Text style={styles.countdownText}>{countdown}</Text>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
    backgroundColor: PRIMARY_COLOR,
  },
  usernameText: {
    color: TEXT_COLOR,
    fontSize: 18,
    fontFamily: 'Press Start 2P',
    marginBottom: 20,
  },
  eyeImage: {
    width: 150,
    height: 150,
    marginBottom: 20,
  },
  eyeImageSmall: {
    width: 100,
    height: 100,
    marginBottom: 10,
  },
  button: {
    backgroundColor: BUTTON_COLOR,
    paddingHorizontal: 30,
    paddingVertical: 10,
    borderRadius: 5,
    borderWidth: 3,
    borderColor: 'white',
    marginBottom: 10,
  },
  buttonText: {
    color: TEXT_COLOR,
    fontSize: 16,
    fontFamily: 'Press Start 2P',
  },
  statusText: {
    color: 'black',
    fontSize: 12,
    fontFamily: 'Press Start 2P',
    height: 20,
    marginBottom: 20,
  },
  navText: {
    color: TEXT_COLOR,
    fontSize: 14,
    fontFamily: 'Press Start 2P',
    marginVertical: 10,
  },
  backButton: {
    alignSelf: 'flex-start',
    position: 'absolute',
    top: 20,
    left: 20,
  },
  label: {
    color: TEXT_COLOR,
    fontSize: 12,
    fontFamily: 'Press Start 2P',
    marginVertical: 10,
  },
  input: {
    backgroundColor: 'white',
    width: '80%',
    padding: 10,
    marginBottom: 20,
    fontFamily: 'Press Start 2P',
  },
  quoteText: {
    color: TEXT_COLOR,
    fontSize: 12,
    fontFamily: 'Press Start 2P',
    marginBottom: 15,
  },
  navRow: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  smallButton: {
    backgroundColor: BUTTON_COLOR,
    padding: 10,
    marginHorizontal: 10,
  },
  buttonTextSmall: {
    color: TEXT_COLOR,
    fontSize: 10,
    fontFamily: 'Press Start 2P',
  },
  title: {
    color: TEXT_COLOR,
    fontSize: 24,
    fontFamily: 'Press Start 2P',
    marginBottom: 20,
  },
  version: {
    color: TEXT_COLOR,
    fontSize: 14,
    fontFamily: 'Press Start 2P',
    marginBottom: 10,
  },
  infoText: {
    color: TEXT_COLOR,
    fontSize: 12,
    fontFamily: 'Press Start 2P',
    textAlign: 'left',
    padding: 10,
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  modalContent: {
    backgroundColor: PRIMARY_COLOR,
    padding: 40,
    borderRadius: 20,
    alignItems: 'center',
  },
  modalText: {
    color: TEXT_COLOR,
    fontSize: 14,
    fontFamily: 'Press Start 2P',
    marginVertical: 20,
  },
  countdownText: {
    color: TEXT_COLOR,
    fontSize: 20,
    fontFamily: 'Press Start 2P',
  },
});

export default App;
