
import app
import de

def Func(arg1, arg2="Alex"):
    print "Ok....", arg1, arg2
    print de.get_row_count()

def Func2():
    print "Func2 called"

app.register_modelling_method("The method...", Func)
app.register_modelling_method("The method2...", Func2)
