package org.jofu.bleva;

import java.util.ArrayList;

import android.content.Context;
import android.os.Debug;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.CheckBox;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

public class BenchmarkAdapter extends ArrayAdapter<Benchmark> {
    private Context context;
    private final static String TAG = "BenchmarkAdapter";

    public BenchmarkAdapter(Context context, ArrayList<Benchmark> benchmarks) {
        super(context, 0, benchmarks);
        this.context = context;

    }

    @Override
    public View getView(final int position, View convertView, ViewGroup parent) {

        RecyclerView.ViewHolder holder = null;
        Log.d(TAG, ""+position);


        // Get the data item for this position
//        final Benchmark benchmark = getItem(position);
        final Benchmark benchmark = DataHolder.getInstance().getBenchmarks().get(position);
        // Check if an existing view is being reused, otherwise inflate the view
        if (convertView == null) {
            convertView = LayoutInflater.from(getContext()).inflate(R.layout.item_benchmark, parent, false);
        }
        // Lookup view for data population
        final TextView benchmarkName = (TextView) convertView.findViewById(R.id.benchmarkName);
        TextView benchmarkDesc = (TextView) convertView.findViewById(R.id.benchmarkDescription);
        // Populate the data into the template view using the data object
        benchmarkName.setText(DataHolder.getInstance().getBenchmarks().get(position).getName());
        benchmarkDesc.setText(DataHolder.getInstance().getBenchmarks().get(position).getDescription());

        CheckBox c = (CheckBox) convertView.findViewById(R.id.benchmarkCheck);
        c.setChecked(DataHolder.getInstance().getBenchmarks().get(position).isSelected());

        c.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                Log.d(TAG, "selected/deselected "+DataHolder.getInstance().getBenchmarks().get(position).getName());
                benchmark.setSelected(!DataHolder.getInstance().getBenchmarks().get(position).isSelected());
                Log.d(TAG, ""+position);
                DataHolder.getInstance().setBenchmark(position, benchmark);
            }
        });


        // Return the completed view to render on screen
        return convertView;
    }
}
