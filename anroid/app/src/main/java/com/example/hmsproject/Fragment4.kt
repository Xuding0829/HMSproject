package com.example.hmsproject

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.Button
import android.widget.ListView
import androidx.fragment.app.Fragment
import com.bumptech.glide.Glide
import com.bumptech.glide.load.resource.bitmap.RoundedCorners
import com.bumptech.glide.request.RequestOptions
import com.example.hmsproject.Adapter.shopListView
import com.youth.banner.Banner
import com.youth.banner.adapter.BannerImageAdapter
import com.youth.banner.holder.BannerImageHolder
import com.youth.banner.indicator.CircleIndicator


// TODO: Rename parameter arguments, choose names that match
// the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
private const val ARG_PARAM1 = "param1"
private const val ARG_PARAM2 = "param2"

/**
 * A simple [Fragment] subclass.
 * Use the [Fragment4.newInstance] factory method to
 * create an instance of this fragment.
 */
class Fragment4 : Fragment() {
    private val titles = arrayOf("恩百蛋白粉", "年华按摩仪", "牛磺酸蛋白口服液", "中老年钙片", "卓越蛋白粉")
    private val prices = arrayOf("价格：49", "价格：69", "价格：65", "价格：32", "价格：89")
    private val icons = intArrayOf(R.drawable.pill1, R.drawable.pill2, R.drawable.pill3, R.drawable.pill4, R.drawable.pill5)

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // 为此片段填充fragment4布局
        val view = inflater.inflate(R.layout.fragment_4, container, false)

        // 查找横幅视图（广告滚动组件）
        val banner: Banner<DataBean, BannerImageAdapter<DataBean>> = view.findViewById(R.id.banner)
        banner.setAdapter(object : BannerImageAdapter<DataBean>(DataBean.testData3) {
            override fun onBindView(holder: BannerImageHolder, data: DataBean, position: Int, size: Int) {
                // 使用Glide加载图片
                Glide.with(holder.itemView)
                    .load(data.imageUrl)
                    .apply(RequestOptions.bitmapTransform(RoundedCorners(30)))
                    .override(banner.width, banner.height) // 设置图片尺寸
                    .into(holder.imageView)
            }
        }).addBannerLifecycleObserver(viewLifecycleOwner) // 添加生命周期观察者
            .setIndicator(CircleIndicator(requireContext())) // 设置指示器

        // 查找ListView
        val mListView: ListView = view.findViewById(R.id.lv)

        // 创建适配器
        val mAdapter = MyBaseAdapter()

        // 设置ListView适配器
        mListView.adapter = mAdapter

        return view
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
            val holder: shopListView.ViewHolder

            // 如果convertView为空，则需要创建一个新的视图
            if (convertView == null) {
                // 通过布局填充器加载自定义的商店列表视图
                convertView = View.inflate(requireContext(), R.layout.shoplist_view_header, null)
                // 创建一个ViewHolder对象来保存视图中的子视图引用
                holder = shopListView.ViewHolder()
                // 初始化ViewHolder中的视图引用
                holder.title = convertView.findViewById(R.id.title)
                holder.price = convertView.findViewById(R.id.price)
                holder.iv = convertView.findViewById(R.id.iv)
                holder.btnBuy = convertView.findViewById<Button>(R.id.btnBuy)
                // 将ViewHolder对象存储在convertView的Tag中，以便在重用时可以直接获取
                convertView.tag = holder
            } else {
                // 如果convertView不为空，则从Tag中获取ViewHolder对象
                holder = convertView.tag as shopListView.ViewHolder
            }



        // 设置点击事件
//            convertView?.setOnClickListener {
//                // 根据位置区分点击事件
//                when (position) {
//                    0 -> {
//
//                    }
//                    1 -> {
//                        // 第二个项的点击事件
//                        // 在这里显示相应的提示信息
//                        //showToast("抱歉，家属目前并未就医")
//                    }
//                    // 添加更多的项的点击事件，如果需要的话
//                }
//            }

            holder.title.text = titles[position]
            holder.price.text = prices[position]
            holder.iv.setBackgroundResource(icons[position])
            return convertView!!
        }
    }

//    internal class ViewHolder {
//        lateinit var title: TextView
//        lateinit var price: TextView
//        lateinit var iv: ImageView
//        lateinit var btnBuy: Button
//    }




    companion object {
        /**
         * Use this factory method to create a new instance of
         * this fragment using the provided parameters.
         *
         * @param param1 Parameter 1.
         * @param param2 Parameter 2.
         * @return A new instance of fragment Fragment4.
         */
        // TODO: Rename and change types and number of parameters
        @JvmStatic
        fun newInstance(param1: String, param2: String) =
            Fragment4().apply {
                arguments = Bundle().apply {
                    putString(ARG_PARAM1, param1)
                    putString(ARG_PARAM2, param2)
                }
            }
    }
}