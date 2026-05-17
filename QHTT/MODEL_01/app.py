from flask import Flask, render_template, request
from scipy.optimize import linprog

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():

    result = None
    error = None

    if request.method == 'POST':

        try:

            # ==========================
            # HÀM MỤC TIÊU
            # ==========================
            c = list(map(float,
                         request.form['objective'].split(',')))

            objective_type = request.form['objective_type']

            # max -> min
            if objective_type == 'max':
                c = [-x for x in c]

            # ==========================
            # RÀNG BUỘC
            # ==========================
            constraints_text = (
                request.form['constraints']
                .strip()
                .split('\n')
            )

            A_ub = []
            b_ub = []

            for line in constraints_text:

                # ví dụ:
                # 1,1,<=,4

                parts = line.split(',')

                coeffs = list(map(float, parts[:-2]))
                sign = parts[-2].strip()
                rhs = float(parts[-1])

                if sign == '<=':

                    A_ub.append(coeffs)
                    b_ub.append(rhs)

                elif sign == '>=':

                    A_ub.append(
                        [-x for x in coeffs]
                    )

                    b_ub.append(-rhs)

                else:
                    raise ValueError(
                        'Chỉ hỗ trợ <= hoặc >='
                    )

            # ==========================
            # BOUNDS
            # ==========================
            bounds = [(0, None)] * len(c)

            # ==========================
            # GIẢI
            # ==========================
            res = linprog(
                c,
                A_ub=A_ub,
                b_ub=b_ub,
                bounds=bounds,
                method='highs'
            )

            if res.success:

                optimal_value = res.fun

                if objective_type == 'max':
                    optimal_value = -optimal_value

                result = {
                    'variables': res.x,
                    'optimal_value': optimal_value
                }

            else:
                error = res.message

        except Exception as e:
            error = str(e)

    return render_template(
        'index.html',
        result=result,
        error=error
    )


if __name__ == '__main__':
    app.run(debug=True)