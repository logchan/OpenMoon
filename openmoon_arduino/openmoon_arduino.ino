#include <FastLED.h>

#define BRIGHTNESS 32

#define N_GROUPS 2
#define N_LEDS 30

#define LED_PIN_0 3
#define LED_PIN_1 4

CRGB leds[N_GROUPS][N_LEDS];

class StringStream: public Stream {
    public:
    StringStream(const String& s): m_idx(0), m_str(String(s)) {

    }

    int available() override {
        return m_idx < m_str.length();
    }

    int read() override {
        return m_idx >= m_str.length() ? -1 : m_str[m_idx++];
    }

    int peek() override {
        return m_idx >= m_str.length() ? -1 : m_str[m_idx];
    }

    size_t write(uint8_t v) override {
        return 0;
    }

    private:
    const String m_str;
    int m_idx;
};

void setup() {
    Serial.begin(115200);

    FastLED.addLeds<WS2812B, LED_PIN_0, GRB>(leds[0], N_LEDS);
    FastLED.addLeds<WS2812B, LED_PIN_1, GRB>(leds[1], N_LEDS);
    FastLED.setBrightness(BRIGHTNESS);
    for (int i = 0; i < N_LEDS; ++i) {
        leds[0][i] = CRGB(255, 255, 255);
    }
    FastLED.show();
}

void handle_set_color(StringStream& line) {
    auto group = line.parseInt();
        Serial.print("["); Serial.print(group); Serial.print("]");
    if (group < 0 || group >= N_GROUPS) {
        return;
    }

    auto idx = line.parseInt();
        Serial.print("["); Serial.print(idx); Serial.print("]");

    if (idx < 0 || idx >= N_LEDS) {
        return;
    }

    auto r = line.parseInt();
    auto g = line.parseInt();
    auto b = line.parseInt();

    leds[group][idx] = CRGB(r, g, b);
}

void handle_set_brightness(StringStream& line) {
    FastLED.setBrightness(line.parseInt());
}

void handle_show(StringStream& line) {
    FastLED.show();
}

#define N_COMMANDS 3
const char* commands[N_COMMANDS] {
    "COL",
    "BRI",
    "SHOW",
};
void (*handlers[N_COMMANDS]) (StringStream&) {
    handle_set_color,
    handle_set_brightness,
    handle_show,
};

void loop() {
    if (!Serial.available()) {
        return;
    }

    auto line = StringStream(Serial.readStringUntil('\n'));
    line.setTimeout(0);
    auto cmd = line.readStringUntil(' ');

    if (cmd.length() > 0 && cmd[cmd.length() - 1] == '\n') {
        cmd = cmd.substring(0, cmd.length() - 1);
    }
    for (int i = 0; i < N_COMMANDS; ++i) {
        if (cmd.equalsIgnoreCase(commands[i])) {
            (*handlers[i])(line);
            break;
        }
    }
}
