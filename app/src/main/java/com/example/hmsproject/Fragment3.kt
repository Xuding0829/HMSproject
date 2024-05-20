package com.example.hmsproject

import android.graphics.BitmapFactory
import android.graphics.drawable.Drawable
import android.os.AsyncTask
import android.os.Bundle
import android.util.Log
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ImageView
import android.widget.TableLayout
import android.widget.TableRow
import android.widget.TextView
import androidx.fragment.app.DialogFragment
import androidx.fragment.app.Fragment
import java.net.URL
import com.bumptech.glide.Glide
import com.bumptech.glide.load.engine.DiskCacheStrategy
import com.bumptech.glide.request.RequestOptions
import kotlinx.serialization.json.Json
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStreamReader
import kotlinx.serialization.*
import kotlinx.serialization.json.*
import java.net.HttpURLConnection
import kotlin.concurrent.thread

// TODO: Rename parameter arguments, choose names that match
// the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
private const val ARG_PARAM1 = "param1"
private const val ARG_PARAM2 = "param2"

/**
 * A simple [Fragment] subclass.
 * Use the [Fragment3.newInstance] factory method to
 * create an instance of this fragment.
 */
class Fragment3 : Fragment() {
    // TODO: Rename and change types of parameters
    private var param1: String? = null
    private var param2: String? = null
    lateinit var reportImageView: ImageView
    lateinit var labImageView: ImageView
    lateinit var textview: TextView
    lateinit var table_drug:TableLayout


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            param1 = it.getString(ARG_PARAM1)
            param2 = it.getString(ARG_PARAM2)
        }
    }



    fun json() {
        @Serializable
        data class Medicine(
            val cautions: String,
            val medicineName: String
        )
        @Serializable
        data class MedicalInfo(
            val medicines: List<Medicine>,
            val suggestion: List<String>
        )

        val jsonString = """
        {
            "1": {
                "medicines": [
                    {
                        "cautions": "250mL 1次/日 静点",
                        "medicineName": "0.9%氯化钠注射剂"
                    },
                    {
                        "cautions": "250mL 1次/日 静点",
                        "medicineName": "5%葡萄糖注射剂"
                    },
                    {
                        "cautions": "",
                        "medicineName": "注射器"
                    }
                ],
                "suggestion": [
                    "作为人工智能助手，我无法提供专业的医疗建议。如果您或他人有健康问题，建议您咨询医生或其他专业医疗人士，以获得适合您具体情况的专业建议。\n同时，保持良好的生活习惯，如适量运动、合理饮食、充足休息，对身体健康也是有益的。"
                ]
            }
        }
        """.trimIndent()

        val json = Json { ignoreUnknownKeys = true }
        try {
            val medicalInfo: Map<String, MedicalInfo> = json.decodeFromString<Map<String, MedicalInfo>>(jsonString)
            val suggestion = medicalInfo["1"]?.suggestion
            suggestion?.forEach { println(it) }
            val suggestionText = suggestion?.joinToString("\n")
            textview.setText(suggestionText)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    fun sendRequestWithHttpURLConnection() {

        thread {
            var connection: HttpURLConnection? = null
            try {
                val response = StringBuilder()
                // val url = URL("https://www.baidu.com")
                val url = URL("https://hms.1149528.xyz/report-files/10000000001/")
                connection = url.openConnection() as HttpURLConnection
               // connection.requestMethod = "GET"
                connection.connectTimeout = 8000
                connection.readTimeout = 8000
                val input = connection.inputStream

                // 下面对获取到的输入流进行读取
                val reader = BufferedReader(InputStreamReader(input))
                reader.use {
                    reader.forEachLine {
                        response.append(it)
                    }
                }

                val tv_doctor_suggestion_content = view?.findViewById<Button>(R.id.tv_doctor_suggestion_content)
                if (tv_doctor_suggestion_content != null) {
                    tv_doctor_suggestion_content.text = response.toString()
                }
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                connection?.disconnect()
            }
        }

            // URL("https://hms.1149528.xyz/report-files/10000000001/")
            // 获取信息的样例 ["0de70d92bc27d90c5b16cb982e21db4a2967.jpg", "135c-kentcvy3153455.jpg"]
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // imgSet
        // 使用布局填充器从fragment3布局文件中实例化视图
        val view = inflater.inflate(R.layout.fragment_3, container, false)

        reportImageView = view.findViewById(R.id.img_report)
        reportImageView.setVisibility(View.GONE)

        labImageView = view.findViewById(R.id.img_lab)
        labImageView.setVisibility(View.GONE)

        textview = view.findViewById(R.id.tv_doctor_suggestion_content)
        textview.setText("暂无数据")

        table_drug = view.findViewById(R.id.table_drug)
        table_drug.setVisibility(View.GONE)


        val sendRequestBtn = view.findViewById<Button>(R.id.sendRequestBtn)
        sendRequestBtn.setOnClickListener {
            // 影像
            reportImageView.setVisibility(View.VISIBLE);
            reportImageView.setOnClickListener {
                showDialogFragment(it as ImageView)
            }
            val reportImageUrl = "https://hms.1149528.xyz/report-files/10000000001/0de70d92bc27d90c5b16cb982e21db4a2967.jpg"
            Glide.with(this)
                .load(reportImageUrl)
                .into(reportImageView)
            // 诊断报告
            labImageView.setVisibility(View.VISIBLE);
            labImageView.setOnClickListener {
                showDialogFragment(it as ImageView)
            }
            val labImageUrl = "https://hms.1149528.xyz/report-files/10000000001/135c-kentcvy3153455.jpg"
            Glide.with(this)
                .load(labImageUrl)
                .into(labImageView)

            table_drug.setVisibility(View.VISIBLE)
            val tableLayout = view.findViewById<TableLayout>(R.id.table_drug)
            // 动态添加TableRow
            fun addTableRow(drugName: String, time: String, dosage: String) {
                val tableRow = TableRow(context)

                val drugTextView = TextView(context).apply {
                    layoutParams = TableRow.LayoutParams(0, TableRow.LayoutParams.WRAP_CONTENT, 1f)
                    text = drugName
                    gravity = Gravity.CENTER
                }

                val timeTextView = TextView(context).apply {
                    layoutParams = TableRow.LayoutParams(0, TableRow.LayoutParams.WRAP_CONTENT, 1f)
                    text = time
                    gravity = Gravity.CENTER
                }

                val dosageTextView = TextView(context).apply {
                    layoutParams = TableRow.LayoutParams(0, TableRow.LayoutParams.WRAP_CONTENT, 1f)
                    text = dosage
                    gravity = Gravity.CENTER
                }

                tableRow.addView(drugTextView)
                tableRow.addView(timeTextView)
                tableRow.addView(dosageTextView)

                tableLayout.addView(tableRow)
            }

            // 调用函数添加药物信息
            addTableRow("阿司匹林肠溶片", "中午", "100mg")
            addTableRow("头孢拉定胶囊", "中午、晚上", "0.25g")

            textview.setText("三餐规律，保证饮食均衡，戒烟戒酒。注意休息，避免劳累、剧烈运动。根据自身情况选择一些中等强度的体育锻炼（如慢跑、骑自行车等），避免剧烈运动。注意室内通风，保持合适的室内湿度（50%～60%），湿度太低容易诱发咳嗽，湿度太高容易滋生病菌。")
        }
        return view
    }

    private fun showDialogFragment(imageView: ImageView) {
        ImageDialogFragment(imageView.drawable).show(childFragmentManager, "imageDialog")
    }

    class ImageDialogFragment(private val drawable: Drawable?) : DialogFragment() { //接受一个drawbale对象（图像或者图形）显示一个对话框，用于展示一个图像
        override fun onCreateView(
            inflater: LayoutInflater,
            container: ViewGroup?,
            savedInstanceState: Bundle?
        ): View? {
            val view = inflater.inflate(R.layout.dialog_image, container, false)
            val imageView = view.findViewById<ImageView>(R.id.dialog_image)
            imageView.setImageDrawable(drawable)
            return view
        }
    }

companion object {
        /**
         * Use this factory method to create a new instance of
         * this fragment using the provided parameters.
         *
         * @param param1 Parameter 1.
         * @param param2 Parameter 2.
         * @return A new instance of fragment Fragment3.
         */
        // TODO: Rename and change types and number of parameters
        @JvmStatic
        fun newInstance(param1: String, param2: String) =
            Fragment3().apply {
                arguments = Bundle().apply {
                    putString(ARG_PARAM1, param1)
                    putString(ARG_PARAM2, param2)
                }
            }
    }
}

