package com.example.hmsproject

import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import com.example.hmsproject.Utils.MqttHelper
import com.google.android.material.slider.Slider

// TODO: Rename parameter arguments, choose names that match
// the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
private const val ARG_PARAM1 = "param1"
private const val ARG_PARAM2 = "param2"

/**
 * A simple [Fragment] subclass.
 * Use the [Fragment1.newInstance] factory method to
 * create an instance of this fragment.
 */
class Fragment1 : Fragment() {   //fragment1即为就诊情况
    // TODO: Rename and change types of parameters
    private var param1: String? = null
    private var param2: String? = null
    private lateinit var mqttHelper2: MqttHelper

    enum class MedicalSteps(val stepName: String) { //枚举类型存放最顶上状态栏显示的文字
        REGISTRATION("当前家属状态：正在挂号"),
        QUEUEING("当前家属状态：排队就医"),
        CONSULTING("当前家属状态：就医中"),
        LAB_TEST("当前家属状态：化验中"),
        MEDICINE_RECEIPT("当前家属状态：取药中"),
        COMPLETED("当前家属状态：已完成");
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            param1 = it.getString(ARG_PARAM1)
            param2 = it.getString(ARG_PARAM2)
        }
        mqttHelper2 = MqttHelper(
            mqttId = "xxx",
            subscriptionTopics = listOf("www"),
            publishTopics = listOf("cyffabu")
        )
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {


        val view = inflater.inflate(R.layout.fragment_1, container, false)
        val button= view.findViewById<Button>(R.id.diaoping)
        button.setOnClickListener {
            val topic = "cyffabu"
            val message = "LEDON"
            mqttHelper2.publishMessage(topic, message)
        }

        val textView = view.findViewById<TextView>(R.id.statusTextView)
        textView.text = MedicalSteps.REGISTRATION.stepName
        val slider = view.findViewById<Slider>(R.id.slider) //sLider控件，用于显示就医进度

        slider.addOnChangeListener { _, value, _ ->
            when (value.toInt()) {
                0 -> {
                    textView.text = MedicalSteps.REGISTRATION.stepName
                }
                1 -> {
                    textView.text = MedicalSteps. QUEUEING.stepName
                }
                2 -> {
                    textView.text = MedicalSteps.CONSULTING.stepName
                }
                3 -> {
                    textView.text = MedicalSteps.LAB_TEST.stepName
                }
                4 -> {
                    textView.text = MedicalSteps. MEDICINE_RECEIPT.stepName
                }
                5 -> {
                    textView.text = MedicalSteps. COMPLETED.stepName
                }
            }
        }


        return view
    }



    companion object {
        /**
         * Use this factory method to create a new instance of
         * this fragment using the provided parameters.
         *
         * @param param1 Parameter 1.
         * @param param2 Parameter 2.
         * @return A new instance of fragment Fragment1.
         */
        // TODO: Rename and change types and number of parameters
        @JvmStatic
        fun newInstance(param1: String, param2: String) =
            Fragment1().apply {
                arguments = Bundle().apply {
                    putString(ARG_PARAM1, param1)
                    putString(ARG_PARAM2, param2)
                }
            }
    }
}