
import de, gmdh, sol

class CriterionInfo:

        def __init__(self, name, description, criterion_instance):
                self.name = name
                self.description = description
                self.criterion_instance = criterion_instance

class ModelInfo:

        def __init__(self, name, description, model_instance):
                self.name = name
                self.description = description
                self.model_instance = model_instance


criterions = [
          CriterionInfo("Regularity", gmdh.RegularitySelector.__doc__, gmdh.RegularitySelector(10)),
          CriterionInfo("Regularity on teach subsample", gmdh.RegularityTeachSelector.__doc__, gmdh.RegularityTeachSelector(10)),
          CriterionInfo("Regularity on all subsamples", gmdh.RegularityFullSelector.__doc__, gmdh.RegularityFullSelector(10)),
          CriterionInfo("Minimum offset", gmdh.MinOffsetSelector.__doc__, gmdh.MinOffsetSelector(10)),
          CriterionInfo("Minimum offset + Regularity", gmdh.MinOfsRegSelector.__doc__, gmdh.MinOfsRegSelector(10))
        ]

models = [
          ModelInfo(gmdh.CovLinPattern.__doc__, gmdh.CovLinPattern.__doc__, gmdh.CovLinPattern()),
          ModelInfo(gmdh.CovMulPattern.__doc__, gmdh.CovMulPattern.__doc__, gmdh.CovMulPattern()),
          ModelInfo(gmdh.CovSqrPattern.__doc__, gmdh.CovSqrPattern.__doc__, gmdh.CovSqrPattern()),
          ModelInfo(gmdh.CovDDPattern.__doc__, gmdh.CovDDPattern.__doc__, gmdh.CovDDPattern()),
          ModelInfo(gmdh.CovDLPattern.__doc__, gmdh.CovDLPattern.__doc__, gmdh.CovDLPattern()),
          ModelInfo(gmdh.CovLDPattern.__doc__, gmdh.CovLDPattern.__doc__, gmdh.CovLDPattern()),
          ModelInfo(gmdh.CovMDDPattern.__doc__, gmdh.CovMDDPattern.__doc__, gmdh.CovMDDPattern()),
          ModelInfo(gmdh.CovMDLPattern.__doc__, gmdh.CovMDLPattern.__doc__, gmdh.CovMDLPattern()),
          ModelInfo(gmdh.CovMLDPattern.__doc__, gmdh.CovMLDPattern.__doc__, gmdh.CovMLDPattern())
        ]




def extract_matrix():
        rc, ac = de.get_row_count(), de.get_arg_count()
        matrix = sol.new_matrix(rc, ac)
        for i in xrange(rc):
          for j in xrange(ac):
            v = de.get_cell(i, j)            
            try:
              matrix(i, j, float(v))
            except:
              matrix(i, j, 1.0e+300)
        return matrix

def extract_ta_cols():
        tcols = []
        acols = []
        for i in xrange(de.get_arg_count()):
          if de.get_is_target(i):
            tcols += [i]
          else:
            acols += [i]
        return tcols, acols

def extract_tck_rows():
        trows = []
        crows = []
        krows = []
        for i in xrange(de.get_row_count()):
          if de.get_row_marker(i) == "Teach":
            trows += [i]
          elif de.get_row_marker(i) == "Check":
            crows += [i]
          elif de.get_row_marker(i) == "Control":
            krows += [i]
        return trows, crows, krows


def on_gmdh_selection(cur_selection, crv_min, selector):
        print "Current selection: %i;  Criterion: %g" % (cur_selection, crv_min)

def start_gmdh(selection_count, best_model_count, criterion_index, model_indexes):
        global models
        criterion = criterions[criterion_index].criterion_instance
        criterion.set_best_model_count(best_model_count)
        use_models = map(lambda x, g_models=models: g_models[x].model_instance, model_indexes)
        target_cols, arg_cols = extract_ta_cols()
        trows, crows, krows = extract_tck_rows()
        matrix = extract_matrix()
        print "WARNING! Starting GMDH..."
        Net = gmdh.gmdh(matrix, target_cols, arg_cols, criterion, use_models, trows, crows, krows, selection_count, on_gmdh_selection)
        Net.input_names = []
        Net.input_dict = {}
        for idx in Net.inputs:
          arg_idx = arg_cols[idx]
          arg_name = de.get_arg_name(arg_idx)
          Net.input_names += [arg_name]
          Net.input_dict[arg_idx] = arg_name
        Net.out_names = []
        Net.out_dict = {}
        for idx in target_cols:
          target_name = de.get_arg_name(idx)
          Net.out_names += [target_name]
          Net.out_dict[idx] = target_name
        print "GMDH finished."
        return Net

