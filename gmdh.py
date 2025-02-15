from sol import *


class GMDHSelector:
        """
                Базовый класс селектора частных описаний.                                
        """   

        def __init__(self, max_model_count = 5):
                """

                Формат вызова конструктора:

                 GMDHSelector( <Макс. кол-во частных описаний> ) 
                   
                """
                self.__max_model_count = max_model_count
                self.clear()

        def set_best_model_count(self, value):
                self.__max_model_count = value
                self.clear()
                

        def get_max_model_count(self):
                return self.__max_model_count

        def get_min_criteria_value(self):
                return self._min_criteria_value

        def clear(self):
                self._items = []
                self._min_criteria_value = None

        def check_subsamples(self, trows, crows, krows):
                raise NotImplementedError()

        def criteria(self, item):
                """
                Возвращает значение критерия для заданного частного
                описания. 
                """
                raise NotImplementedError()

        def add(self, item):
                """
                Добавляет частное описание в список, при условии, что
                его критерий меньше, чем у уже имеющихся в списке описаний,
                либо список еще не полон.
                """
                items = self._items        
                try:
                        crv = self.criteria(item)
                        minv = self._min_criteria_value
                        if len(items) < self.__max_model_count:                 
                                j = 0
                                added = 0
                                for c, i in items:                             
                                        if crv < c:
                                                items.insert(j, (crv, item))
                                                added = 1
                                                break
                                        j += 1
                                if not added:
                                        items.append((crv, item))
                                if minv is None or crv < minv:
                                        self._min_criteria_value = crv
                                return item
                        else:
                                if crv < minv:
                                        items.insert(0, (crv, item))
                                        self._min_criteria_value = crv
                                        del items[-1]
                                        return item
                except ArithmeticError:
                        pass

                                                                                                                      
        def get_items(self):
                """
                Возвращает список частных описаний со значениями критериев.
                """
                return self._items


class RegularitySelector(GMDHSelector):
        """Regularity criterion.\nEuclid norm of model output on check subsample."""

        def check_subsamples(self, trows, crows, krows):
                if len(crows) == 0:
                        raise RuntimeError("For regulerity criterion check subsample needed.")

        def criteria(self, item):
                """
                У 'item' должны быть следующие поля:
                

                check_rows      - список индексов строк проверочной последовательности.
                target          - матрица целевых аргументов.
                out             - матрица выхода модели.

                """
                cr = item.check_rows
                check_out = item.out.rows(cr)
                check_target = item.target.rows(cr)
                return sum_sqddsq(check_out, check_target, check_target)

class RegularityTeachSelector(GMDHSelector):
        """Regularity criterion on teach subsample.\nEuclid norm of model output on teach subsample."""

        def check_subsamples(self, trows, crows, krows):
                pass

        def criteria(self, item):
                """
                У 'item' должны быть следующие поля:
                

                target_rows     - список индексов строк обучающей последовательности.
                teach_target    - матрица целевых аргументов обуч. последовательности.
                out             - матрица выхода модели на обуч. последовательности.

                """
                tr = item.teach_rows
                tt = item.teach_target
                return sum_sqddsq(item.out.rows(tr), tt, tt)

class RegularityFullSelector(GMDHSelector):
        """Regularity criterion on all subsamples.\nEuclid norm of model output on all subsamples."""

        def check_subsamples(self, trows, crows, krows):
                pass

        def criteria(self, item):
                """
                У 'item' должны быть следующие поля:
                
                out             - матрица выхода модели на обуч. последовательности.
                target          - матрица целевого аргумента.

                """
                t = item.target
                return sum_sqddsq(item.out, t, t)

                
class MinOffsetSelector(GMDHSelector):
        """Minimal offset criterion.\nCalculated as difference of model's out teached\non teach subsample, and model's\nout teached on check subsample."""

        def check_subsamples(self, trows, crows, krows):
                if len(crows) == 0 or len(trows) == 0:
                        raise RuntimeError("For minimal offset criterion check and teach subsamples needed.")

        def criteria(self, item):
                """
                Возвращает значение критерия минимума смещения.

                У 'item' должны быть следующие поля:

                check_rows      - список индексов строк проверочной последовательности.
                target          - матрица целевых аргументов.
                pargs           - матрица аргументов, приведенная к pattern-у, с 
                                  помощью которого была сгенерирована модель на проверочной 
                                  последовательности.
                target          - матрица целевых аргументов.
                out             - матрица выхода модели.
                """
                cr = item.check_rows
                check_pargs = item.pargs.rows(cr)
                check_target = item.target.rows(cr)
                croots = lsq(check_pargs, check_target)
                return sum_sqddsq(item.pargs*croots, item.out, item.target)


class MinOfsRegSelector(GMDHSelector):
        """
        Критерий минимума смещения плюс регулярность.

          Расчитывается как сумма критериев регулярности и минимума смещения.

          Рекомендации к применению: используется для задач поиска физических 
        моделей.
        """

        def check_subsamples(self, trows, crows, krows):
                if len(crows) == 0 or len(trows) == 0:
                        raise RuntimeError("For minimal offset + regularity criterion check and teach subsamples needed.")

        def criteria(self, item):
                """
                Возвращает значение критерия минимума смещения плюс регулярность.

                У 'item' должны быть следующие поля:


                check_rows      - список индексов строк проверочной последовательности.
                target          - матрица целевых аргументов.
                pargs           - матрица аргументов, приведенная к pattern-у, с 
                                  помощью которого была сгенерирована модель на проверочной 
                                  последовательности.
                target          - матрица целевых аргументов.
                out             - матрица выхода модели.
                """
                cr = item.check_rows
                check_pargs = item.pargs.rows(cr)
                check_target = item.target.rows(cr)
                check_out = item.out.rows(cr)
                croots = lsq(check_pargs, check_target)
                minofs = sum_sqddsq(item.pargs*croots, item.out, item.target)
                return minofs + sum_sqddsq(check_out, check_target, check_target)




class BasePattern:

        def get_arg_count(self):
                raise NotImplementedError()

        def patternize(self, item):
                raise NotImplementedError()


class CovPattern(BasePattern):
        
        def get_arg_count(self):
                return 2
        

class CovLinPattern(CovPattern):
        """F(x, y) = a0 + a1*x + a2*y"""

        def patternize(self, item):
                return cov_lin_matrix(item)

class CovMulPattern(CovPattern):
        """F(x, y) = a0 + a1*x + a2*y + a3*x*y"""

        def patternize(self, item):
                return cov_mul_matrix(item)

class CovSqrPattern(CovPattern):
        """F(x, y) = a0 + a1*x + a2*y + a3*x*y + a4*x^2 + a5*y^2"""

        def patternize(self, item):
                return cov_sqr_matrix(item)

class CovDDPattern(CovPattern):
        """F(x, y) = a0 + a1/x + a2/y"""

        def patternize(self, item):
                return cov_dd_matrix(item)

class CovDLPattern(CovPattern):
        """F(x, y) = a0 + a1/x + a2*y"""

        def patternize(self, item):
                return cov_dl_matrix(item)

class CovLDPattern(CovPattern):
        """F(x, y) = a0 + a1*x + a2/y"""

        def patternize(self, item):
                return cov_ld_matrix(item)

class CovMDDPattern(CovPattern):
        """F(x, y) = a0 + a1/x*y"""

        def patternize(self, item):
                return cov_mdd_matrix(item)

class CovMDLPattern(CovPattern):
        """F(x, y) = a0 + a1*y/x"""

        def patternize(self, item):
                return cov_mdl_matrix(item)

class CovMLDPattern(CovPattern):
        """F(x, y) = a0 + a1*x/y"""

        def patternize(self, item):
                return cov_mld_matrix(item)


def _filter_models(root, models):
        arg_indexes = root.arg_indexes
        R = [root]
        for model in models:
          for ai in arg_indexes:
            if ai in model.out_indexes:
              X = _filter_models(model, models)
              for x in X:
                if x not in R:
                  R += [x]
        return R


class InductiveNet:

        def __init__(self, models, arg_count):
                self.arg_count = arg_count
                # Находим корневую модель
                root = min(map(lambda model: (model.crv, model), models))[1]
                self.root = root.copy()
                self.root.arg_indexes = root.arg_indexes
                self.root.out_indexes = root.out_indexes
                self.root.pattern = root.pattern
                self.root.crv = root.crv
                # Фильтруем модели (убираем ненужные)
                models = _filter_models(root, models)
                # Упорядочиваем модели по порядку расчетов
                models = map(lambda model: (list(model.out_indexes), model), models)
                models.sort()
                models = map(lambda x: x[1], models)
                self.models = []
                for model in models:
                        m2 = model.copy()
                        m2.arg_indexes = model.arg_indexes
                        m2.out_indexes = model.out_indexes
                        m2.pattern = model.pattern
                        m2.crv = model.crv
                        self.models += [m2]
                self.inputs = []
                self.outputs = []
                for model in self.models:
                  self.outputs += list(model.out_indexes)
                  for ai in model.arg_indexes:
                    if ai not in self.inputs and ai < self.arg_count:
                      self.inputs += [ai]
                self.inputs.sort()

        def out(self, args):
                out_count = len(self.outputs)
                in_count = len(self.inputs)
                inputs = self.inputs
                outputs = self.outputs
                if in_count != args.col_count:
                        raise TypeError("Network input count is %i, given %i" % (in_count, args.col_count))
                wm = new_matrix(args.row_count, args.col_count + out_count)
                wm.clear()
                col_mapping = {}
                for i in xrange(in_count):
                        wm[i] = args[i]
                        col_mapping[inputs[i]] = i
                i = in_count
                for j in xrange(out_count):
                        col_mapping[outputs[j]] = i
                        i += 1
                i = in_count 
                for model in self.models:
                        arg_indexes = model.arg_indexes
                        new_indexes = map(lambda index, mapping=col_mapping: mapping[index], arg_indexes)
                        args = wm.cols(new_indexes)
                        pargs = model.pattern.patternize(args)
                        mul_to(pargs, model, wm, 0, i)
                        i += model.col_count
                return wm.cols(map(lambda index, mapping=col_mapping: mapping[index], self.root.out_indexes))

        __call__ = out

                
def gmdh(
          data,
          target_cols, 
          arg_cols,
          selector,
          pattern_list,
          teach_rows,
          check_rows,
          control_rows = None,
          max_selections = 5,
          on_selection_proc = None
        ):
  selector.check_subsamples(teach_rows, check_rows, control_rows)
  arg_count = len(arg_cols)
  best_model_count = selector.get_max_model_count()
  target_count = len(target_cols)
  target = data.cols(target_cols).copy()
  teach_target = target.rows(teach_rows)
  check_target = None
  if check_rows:
    check_target = target.rows(check_rows)
  control_target = None
  if control_rows:
    control_target = target.rows(control_rows)
  args = new_matrix(data.row_count, arg_count + max_selections*best_model_count*target_count)
  args.clear()  
  xargs = data.cols(arg_cols)
  for i in xrange(arg_count):
    args[i] = xargs[i]
  iterators = [(pattern, new_cmi_colref2(args, pattern.get_arg_count())) for pattern in pattern_list]
  current_selection = 0
  current_arg_count = arg_count
  last_criteria_value = None
  best_models = []
  while current_selection < max_selections:
    for pattern, iterator in iterators:
      patternize = pattern.patternize
      work_matrix = iterator.buffer
      while iterator.iterable:
        pargs = patternize(work_matrix)
        teach_pargs = pargs.rows(teach_rows)
        indexes = iterator.indexes
        try:       
          roots = lsq(teach_pargs, teach_target)          
          roots.pattern = pattern
          roots.teach_rows = teach_rows
          roots.check_rows = check_rows
          roots.control_rows = control_rows
          roots.teach_target = teach_target
          roots.check_target = check_target
          roots.control_target = control_target
          roots.teach_pargs = teach_pargs
          roots.out = pargs*roots
          roots.pargs = pargs
          roots.target = target
          roots.arg_indexes = indexes
          selector.add(roots)
        except ArithmeticError:
          pass
        # Если дошли до конца очередного слоя - прекращаем.
        if indexes[-1] == current_arg_count-1 and indexes[0] == current_arg_count-len(indexes):
          break
    min_criteria_value = selector.get_min_criteria_value()
    if min_criteria_value == None:          # Если нет моделей прекратить.
      break
    # Если изменения критерия очень малы - прекратить
    if last_criteria_value != None and abs(min_criteria_value-last_criteria_value) < 1.0e-6:
      break
    # Если первый слой, или критерий уменьшается - установить значение критерия.
    if last_criteria_value == None or min_criteria_value < last_criteria_value:
      last_criteria_value = min_criteria_value
    else:                               # ... иначе прекращаем.
      break
    models = selector.get_items()
    for crv, model in models:
      out = model.out
      model.crv = crv
      tmp = current_arg_count
      for i in xrange(out.col_count):          
        args[current_arg_count] = out[i]
        current_arg_count += 1
      model.out_indexes = range(tmp, current_arg_count)
      best_models += [model]
    if on_selection_proc:
      on_selection_proc(current_selection, min_criteria_value, selector)
    selector.clear()
    current_selection += 1
  if len(best_models) > 0:
    return InductiveNet(best_models, arg_count)
  raise Exception("Inductive net cannot be built. May be there is no anough data.")
  



