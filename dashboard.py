import plotly.express as px
import plotly.graph_objects as go

class PieChart:
    @staticmethod
    def nutrient_breakdown(df):
        data = df[['protein', 'fats', 'carbs', 'fiber', 'sugar', 'iron']].sum()
        fig = px.pie(values=data.values, names=data.index, color_discrete_sequence=['#9DC08B', '#98fb98', '#3A7D44', '#50c878', '#0D4715', '#32c232'])
        return fig.to_html(full_html=False)

class LineChart:
    @staticmethod
    def calories_over_time(df):
        fig = px.line(df, x='date', y='calories', color_discrete_sequence=['#3F7D58'])
        fig.update_layout(plot_bgcolor='#ecfae5')
        return fig.to_html(full_html=False)

class Table:
    @staticmethod
    def nutrient_table(df):
        return df.to_html(classes='table table-responsive', index=False)
    
class KPI:
    @staticmethod
    def kpi(today_df):
        if today_df.empty:
            return " No Data to Display"

        fig = go.Figure()

        nutrients_to_display = ['calories', 'protein', 'fats', 'carbs', 'fiber', 'sugar']

        for i, nutrient in enumerate(nutrients_to_display):
            fig.add_trace(go.Indicator(
                mode="number",
                value=float(today_df[nutrient].iloc[0]),
                title={"text": nutrient.capitalize()},
                domain={'row': i // 3, 'column': i % 3},
                number_font_color='#3e5f3f  ', 
                title_font_color='green'
            ))

        fig.update_layout(
            grid={'rows': 2, 'columns': 3, 'pattern': "independent"},
            height=400
        )

        return fig.to_html(full_html=False) 

