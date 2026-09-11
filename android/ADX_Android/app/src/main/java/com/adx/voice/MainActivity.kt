package com.adx.voice

import android.Manifest
import android.content.pm.PackageManager
import android.media.*
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import okhttp3.*
import okio.ByteString
import org.json.JSONObject
import java.util.Base64
import java.util.concurrent.TimeUnit
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {
    private lateinit var status: TextView
    private lateinit var keyInput: EditText
    private lateinit var button: Button
    private var ws: WebSocket? = null
    private var recording = false
    private var playing = false
    private var audioRecord: AudioRecord? = null
    private var audioTrack: AudioTrack? = null

    private val model = "gemini-3.1-flash-live-preview"
    private val instruction = """
You are ADX, a cute, caring female voice assistant. Always speak in Hindi or natural Hinglish. Be warm, friendly and helpful. Address the user naturally as janu, sona or baby when appropriate. Your name is ADX.
""".trimIndent()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(40, 50, 40, 30); setBackgroundColor(0xFF10131A.toInt()) }
        val title = TextView(this).apply { text = "ADX"; textSize = 42f; setTextColor(0xFFFFFFFF.toInt()); gravity = 1 }
        val sub = TextView(this).apply { text = "Gemini Live Voice Assistant"; textSize = 16f; setTextColor(0xFFB9C0CC.toInt()); gravity = 1 }
        keyInput = EditText(this).apply { hint = "Paste Gemini API key"; setTextColor(0xFFFFFFFF.toInt()); setHintTextColor(0xFF8C94A3.toInt()); inputType = 0x81 }
        button = Button(this).apply { text = "START ADX"; setOnClickListener { if (recording) stop() else start() } }
        status = TextView(this).apply { text = "API key डालें और START ADX दबाएँ"; textSize = 15f; setTextColor(0xFFFFFFFF.toInt()); setPadding(0,30,0,0) }
        root.addView(title); root.addView(sub); root.addView(keyInput); root.addView(button); root.addView(status)
        setContentView(root)
    }

    private fun start() {
        val key = keyInput.text.toString().trim()
        if (key.isEmpty()) { status.text = "पहले Gemini API key डालें"; return }
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.RECORD_AUDIO), 10); return
        }
        connect(key)
    }

    private fun connect(key: String) {
        status.text = "Connecting..."
        val client = OkHttpClient.Builder().pingInterval(20, TimeUnit.SECONDS).build()
        val url = "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key=$key"
        val request = Request.Builder().url(url).build()
        ws = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                val setup = JSONObject().apply {
                    put("setup", JSONObject().apply {
                        put("model", "models/$model")
                        put("generationConfig", JSONObject().apply { put("responseModalities", org.json.JSONArray().put("AUDIO")) })
                        put("systemInstruction", JSONObject().apply { put("parts", org.json.JSONArray().put(JSONObject().put("text", instruction))) })
                        put("speechConfig", JSONObject().apply { put("voiceConfig", JSONObject().apply { put("prebuiltVoiceConfig", JSONObject().put("voiceName", "Laomedeia")) }) })
                        put("inputAudioTranscription", JSONObject())
                        put("outputAudioTranscription", JSONObject())
                    })
                }
                webSocket.send(setup.toString())
                runOnUiThread { status.text = "Connected! बोलना शुरू करें 🎤"; button.text = "STOP ADX" }
                startAudio()
            }
            override fun onMessage(webSocket: WebSocket, text: String) { handleMessage(text) }
            override fun onMessage(webSocket: WebSocket, bytes: ByteString) { handleMessage(bytes.utf8()) }
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                stopAudio(); runOnUiThread { status.text = "Connection error: ${t.message}"; button.text = "START ADX" }
            }
            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) { stopAudio(); runOnUiThread { status.text = "Disconnected"; button.text = "START ADX" } }
        })
    }

    private fun handleMessage(text: String) {
        try {
            val root = JSONObject(text); val sc = root.optJSONObject("serverContent") ?: return
            val turn = sc.optJSONObject("modelTurn")
            val parts = turn?.optJSONArray("parts")
            if (parts != null) for (i in 0 until parts.length()) {
                val p = parts.getJSONObject(i); val data = p.optJSONObject("inlineData")?.optString("data") ?: continue
                val audio = Base64.getDecoder().decode(data); if (audio.isNotEmpty()) play(audio)
            }
            val out = sc.optJSONObject("outputTranscription")?.optString("text")
            if (!out.isNullOrBlank()) runOnUiThread { status.text = "ADX: $out" }
            val inp = sc.optJSONObject("inputTranscription")?.optString("text")
            if (!inp.isNullOrBlank()) runOnUiThread { status.text = "You: $inp" }
        } catch (_: Exception) { }
    }

    private fun startAudio() {
        recording = true
        val min = AudioRecord.getMinBufferSize(16000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT)
        audioRecord = AudioRecord(MediaRecorder.AudioSource.VOICE_COMMUNICATION, 16000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT, maxOf(min, 6400))
        audioRecord!!.startRecording()
        thread(start=true, name="ADX-Mic") {
            val buf = ByteArray(320 * 2)
            while (recording) {
                val n = audioRecord?.read(buf, 0, buf.size) ?: 0
                if (n > 0 && !playing) {
                    val b64 = Base64.getEncoder().encodeToString(buf.copyOf(n))
                    ws?.send(JSONObject().apply { put("realtimeInput", JSONObject().put("audio", JSONObject().apply { put("data", b64); put("mimeType", "audio/pcm;rate=16000") })) }.toString())
                }
            }
        }
    }

    private fun play(data: ByteArray) {
        if (!playing) {
            val min = AudioTrack.getMinBufferSize(24000, AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT)
            audioTrack = AudioTrack.Builder().setAudioAttributes(AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_MEDIA).setContentType(AudioAttributes.CONTENT_TYPE_SPEECH).build()).setAudioFormat(AudioFormat.Builder().setSampleRate(24000).setEncoding(AudioFormat.ENCODING_PCM_16BIT).setChannelMask(AudioFormat.CHANNEL_OUT_MONO).build()).setBufferSizeInBytes(maxOf(min, 9600)).setTransferMode(AudioTrack.MODE_STREAM).build()
            audioTrack!!.play(); playing = true
        }
        audioTrack?.write(data, 0, data.size)
        playing = false
    }

    private fun stop() { ws?.close(1000, "User stopped"); stopAudio(); button.text = "START ADX"; status.text = "ADX stopped" }
    private fun stopAudio() { recording = false; try { audioRecord?.stop() } catch (_: Exception) {}; audioRecord?.release(); audioRecord = null; try { audioTrack?.stop() } catch (_: Exception) {}; audioTrack?.release(); audioTrack = null; playing = false }
    override fun onDestroy() { stop(); super.onDestroy() }
}
