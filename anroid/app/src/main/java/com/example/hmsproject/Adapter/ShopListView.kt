package com.example.hmsproject.Adapter

import android.app.Activity
import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.Button
import android.widget.ImageView
import android.widget.ListView
import android.widget.TextView
import android.widget.Toast
import com.example.hmsproject.R

class shopListView : Activity() {
    private val titles = arrayOf("恩百蛋白粉", "年华按摩仪", "牛磺酸蛋白口服液", "中老年钙片", "卓越蛋白粉")
    private val prices = arrayOf("价格：49", "价格：69", "价格：65", "价格：32", "价格：89")
    private val icons = intArrayOf(
        R.drawable.pill1,
        R.drawable.pill2,
        R.drawable.pill3,
        R.drawable.pill4,
        R.drawable.pill5
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.fragment_4)

        val mListView: ListView = findViewById(R.id.lv)

        val mAdapter = MyBaseAdapter()

        mListView.adapter = mAdapter
    }

    inner class MyBaseAdapter : BaseAdapter() {
        override fun getCount(): Int {
            return titles.size
        }

        override fun getItem(position: Int): Any {
            return titles[position]
        }

        override fun getItemId(position: Int): Long {
            return position.toLong()
        }

        override fun getView(position: Int, convertView: View?, parent: ViewGroup?): View {
            var convertView = convertView
            val holder: ViewHolder
            if (convertView == null) {
                convertView = View.inflate(this@shopListView, R.layout.shoplist_view_header, null)
                    holder = ViewHolder()
                    holder.title = convertView.findViewById(R.id.title)
                    holder.price = convertView.findViewById(R.id.price)
                    holder.iv = convertView.findViewById(R.id.iv)
                    holder.btnBuy = convertView.findViewById(R.id.btnBuy)
                    convertView.tag = holder
                } else {
                holder = convertView.tag as ViewHolder
            }

                    // 设置点击事件
            convertView?.setOnClickListener {
                // 根据位置区分点击事件
                when (position) {
                    0 -> {
                        // 第一个项的点击事件

                    }
                    1 -> {
                        // 第二个项的点击事件
                    }
                    // 可添加更多的项的点击事件
                }
            }

            holder.title.text = titles[position]
            holder.price.text = prices[position]
            holder.iv.setBackgroundResource(icons[position])

            return convertView!!
        }
    }

    internal class ViewHolder {
        lateinit var title: TextView
        lateinit var price: TextView
        lateinit var iv: ImageView
        lateinit var btnBuy: Button
    }

    private fun showToast(message: String) {
        // 在这里实现显示提示信息的逻辑，可以使用 Toast 或其他方式
        // 示例中直接使用 Toast，你可以根据需要进行修改
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
}
